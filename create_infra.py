import boto3
import base64

ec2 = boto3.client('ec2')
autoscaling = boto3.client('autoscaling')

# === USER DATA SCRIPT ===
user_data_script = '''#!/bin/bash
yum update -y
amazon-linux-extras install docker -y
service docker start
usermod -a -G docker ec2-user
yum install -y aws-cli
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 975050024946.dkr.ecr.ap-south-1.amazonaws.com
docker pull 975050024946.dkr.ecr.ap-south-1.amazonaws.com/mern-backend-helloservice:latest
docker run -d -p 80:5000 975050024946.dkr.ecr.ap-south-1.amazonaws.com/mern-backend-helloservice:latest
'''

encoded_user_data = base64.b64encode(user_data_script.encode('utf-8')).decode('utf-8')

def create_vpc():
    vpc_response = ec2.create_vpc(CidrBlock='10.0.0.0/16')
    vpc_id = vpc_response['Vpc']['VpcId']
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': True})
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})
    print(f"Created VPC: {vpc_id}")
    return vpc_id

def create_subnet(vpc_id):
    subnet = ec2.create_subnet(
        CidrBlock='10.0.1.0/24',
        VpcId=vpc_id,
        AvailabilityZone='ap-south-1a')
    subnet_id = subnet['Subnet']['SubnetId']
    ec2.modify_subnet_attribute(
        SubnetId=subnet_id,
        MapPublicIpOnLaunch={'Value': True}
    )
    print(f"Created Subnet: {subnet_id}")
    return subnet_id

def create_security_group(vpc_id):
    sg = ec2.create_security_group(
        GroupName='tanujWebSG',
        Description='Allow HTTP and SSH',
        VpcId=vpc_id)
    sg_id = sg['GroupId']

    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])
    print(f"Created Security Group: {sg_id}")
    return sg_id

def create_launch_template(sg_id):
    lt = ec2.create_launch_template(
        LaunchTemplateName='tanujWebAppLT',
        LaunchTemplateData={
            'ImageId': 'ami-0d03cb826412c6b0f',  # replace with your AMI
            'InstanceType': 't2.micro',
            'SecurityGroupIds': [sg_id],
            'KeyName': 'tanuj-ec2-key',  # replace with your key name
            'UserData': ''  # optional
        })
    launch_template_id = lt['LaunchTemplate']['LaunchTemplateId']
    print(f"Created Launch Template: {launch_template_id}")
    return launch_template_id

def create_asg(launch_template_id, subnet_id):
    autoscaling.create_auto_scaling_group(
        AutoScalingGroupName='tanujWebAppASG',
        LaunchTemplate={
            'LaunchTemplateId': launch_template_id,
            'Version': '$Latest'
        },
        MinSize=1,
        MaxSize=3,
        DesiredCapacity=2,
        VPCZoneIdentifier=subnet_id,
        Tags=[
            {
                'Key': 'Name',
                'Value': 'tanujWebAppInstance',
                'PropagateAtLaunch': True
            }
        ]
    )
    print("Created Auto Scaling Group")

def create_internet_gateway(vpc_id):
    igw = ec2.create_internet_gateway()
    igw_id = igw['InternetGateway']['InternetGatewayId']
    ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    print(f"Created and Attached IGW: {igw_id}")
    return igw_id

def create_route_table(vpc_id, subnet_id, igw_id):
    route_table = ec2.create_route_table(VpcId=vpc_id)
    rt_id = route_table['RouteTable']['RouteTableId']
    
    # Add route to IGW (0.0.0.0/0)
    ec2.create_route(
        RouteTableId=rt_id,
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=igw_id
    )

    # Associate with the subnet
    ec2.associate_route_table(SubnetId=subnet_id, RouteTableId=rt_id)
    print(f"Created Route Table {rt_id} and associated it with Subnet")


def main():
    vpc_id = create_vpc()
    subnet_id = create_subnet(vpc_id)
    igw_id = create_internet_gateway(vpc_id)
    create_route_table(vpc_id, subnet_id, igw_id)
    sg_id = create_security_group(vpc_id)
    launch_template_id = create_launch_template(sg_id)
    create_asg(launch_template_id, subnet_id)

if __name__ == '__main__':
    main()

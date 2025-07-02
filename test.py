import boto3
import base64

ec2 = boto3.client('ec2', region_name='ap-south-1')
autoscaling = boto3.client('autoscaling', region_name='ap-south-1')

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
    vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
    vpc_id = vpc['Vpc']['VpcId']
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': True})
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})
    print(f"[✔] Created VPC: {vpc_id}")
    return vpc_id

def create_subnet(vpc_id):
    subnet = ec2.create_subnet(
        VpcId=vpc_id,
        CidrBlock='10.0.1.0/24',
        AvailabilityZone='ap-south-1a')
    subnet_id = subnet['Subnet']['SubnetId']
    print(f"[✔] Created Subnet: {subnet_id}")
    return subnet_id

def create_security_group(vpc_id):
    sg = ec2.create_security_group(
        GroupName='backend-web-sg',
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
    print(f"[✔] Created Security Group: {sg_id}")
    return sg_id

def create_launch_template(sg_id, user_data_encoded):
    response = ec2.create_launch_template(
        LaunchTemplateName='backend-launch-template',
        LaunchTemplateData={
            'ImageId': 'ami-0f918f7e67a3323f0',  # Amazon Linux 2 in ap-south-1
            'InstanceType': 't2.micro',
            'SecurityGroupIds': [sg_id],
            'KeyName': 'tanuj-ec2-key',  # Replace with your actual key
            'UserData': user_data_encoded
        })
    lt_id = response['LaunchTemplate']['LaunchTemplateId']
    print(f"[✔] Created Launch Template: {lt_id}")
    return lt_id

def create_asg(launch_template_id, subnet_id):
    autoscaling.create_auto_scaling_group(
        AutoScalingGroupName='backend-asg',
        LaunchTemplate={
            'LaunchTemplateId': launch_template_id,
            'Version': '$Latest'
        },
        MinSize=1,
        MaxSize=2,
        DesiredCapacity=1,
        VPCZoneIdentifier=subnet_id,
        Tags=[
            {
                'Key': 'Name',
                'Value': 'mern-backend-instance',
                'PropagateAtLaunch': True
            }
        ]
    )
    print("[✔] Created Auto Scaling Group")

def main():
    vpc_id = create_vpc()
    subnet_id = create_subnet(vpc_id)
    sg_id = create_security_group(vpc_id)
    lt_id = create_launch_template(sg_id, encoded_user_data)
    create_asg(lt_id, subnet_id)

if __name__ == '__main__':
    main()

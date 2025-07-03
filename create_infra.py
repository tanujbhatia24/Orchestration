import boto3
import base64

ec2 = boto3.client('ec2')
autoscaling = boto3.client('autoscaling')

# === Backend User Data ===
backend_user_data = '''#!/bin/bash
sudo yum update -y
sudo yum install docker -y
systemctl enable docker
systemctl start docker
sudo usermod -aG docker ec2-user
# Install AWS CLI v2 (if not already available)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 975050024946.dkr.ecr.ap-south-1.amazonaws.com
docker pull 975050024946.dkr.ecr.ap-south-1.amazonaws.com/mern-backend-helloservice:latest
docker run -d -p 80:3000 975050024946.dkr.ecr.ap-south-1.amazonaws.com/mern-backend-helloservice:latest
'''

# === Frontend User Data ===
frontend_user_data = '''#!/bin/bash
sudo yum update -y
sudo yum install docker -y
systemctl enable docker
systemctl start docker
sudo usermod -aG docker ec2-user
# Install AWS CLI v2 (if not already available)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 975050024946.dkr.ecr.ap-south-1.amazonaws.com
docker pull 975050024946.dkr.ecr.ap-south-1.amazonaws.com/mern-frontend:latest
docker run -d -p 80:3000 975050024946.dkr.ecr.ap-south-1.amazonaws.com/mern-frontend:latest
'''

def create_vpc():
    vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
    vpc_id = vpc['Vpc']['VpcId']
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': True})
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})
    print(f"✅ Created VPC: {vpc_id}")
    return vpc_id

def create_subnets(vpc_id):
    availability_zones = ['ap-south-1a', 'ap-south-1b', 'ap-south-1c']
    cidr_blocks = ['10.0.1.0/24', '10.0.2.0/24', '10.0.3.0/24']  # Unique CIDRs per subnet
    subnet_ids = []

    for az, cidr in zip(availability_zones, cidr_blocks):
        subnet = ec2.create_subnet(
            CidrBlock=cidr,
            VpcId=vpc_id,
            AvailabilityZone=az
        )
        subnet_id = subnet['Subnet']['SubnetId']
        ec2.modify_subnet_attribute(
            SubnetId=subnet_id,
            MapPublicIpOnLaunch={'Value': True}
        )
        subnet_ids.append(subnet_id)
        print(f"✅ Created Subnet in {az}: {subnet_id}")

    return subnet_ids  # list of all subnet IDs


def create_internet_gateway(vpc_id):
    igw = ec2.create_internet_gateway()
    igw_id = igw['InternetGateway']['InternetGatewayId']
    ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    print(f"✅ Created & Attached IGW: {igw_id}")
    return igw_id

def create_route_table(vpc_id, subnet_id, igw_id):
    rt = ec2.create_route_table(VpcId=vpc_id)
    rt_id = rt['RouteTable']['RouteTableId']
    ec2.create_route(RouteTableId=rt_id, DestinationCidrBlock='0.0.0.0/0', GatewayId=igw_id)
    ec2.associate_route_table(SubnetId=subnet_id, RouteTableId=rt_id)
    print(f"✅ Created Route Table and Associated to Subnet")
    return rt_id

def create_security_group(vpc_id):
    sg = ec2.create_security_group(
        GroupName='tanujWebSG',
        Description='Allow HTTP and SSH',
        VpcId=vpc_id
    )
    sg_id = sg['GroupId']
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])
    print(f"✅ Created Security Group: {sg_id}")
    return sg_id

def create_backend_launch_template(sg_id):
    encoded = base64.b64encode(backend_user_data.encode()).decode()
    lt = ec2.create_launch_template(
        LaunchTemplateName='tanujbackendLT',
        LaunchTemplateData={
            'ImageId': 'ami-0d03cb826412c6b0f',
            'InstanceType': 't2.micro',
            'SecurityGroupIds': [sg_id],
            'KeyName': 'tanuj-ec2-key',
            'IamInstanceProfile': {
                'Name': 'tanujEC2ECRAccessRole'  # ✅ Make sure this matches the role name
            },
            'UserData': encoded
        })
    print(f"Created Backend Launch Template")
    return lt['LaunchTemplate']['LaunchTemplateId']

def create_asg(launch_template_id, subnet_ids):
    autoscaling.create_auto_scaling_group(
        AutoScalingGroupName='tanujbackendASG',
        LaunchTemplate={
            'LaunchTemplateId': launch_template_id,
            'Version': '$Latest'
        },
        MinSize=1,
        MaxSize=3,
        DesiredCapacity=2,
        VPCZoneIdentifier=','.join(subnet_ids),  # supports multiple subnets
        Tags=[
            {
                'Key': 'Name',
                'Value': 'tanujbackendInstance',
                'PropagateAtLaunch': True
            }
        ]
    )
    print("✅ Created Auto Scaling Group for backend")


def launch_frontend_instance(subnet_id, sg_id):
    encoded = base64.b64encode(frontend_user_data.encode()).decode()
    instance = ec2.run_instances(
        ImageId='ami-0d03cb826412c6b0f',
        InstanceType='t2.micro',
        KeyName='tanuj-ec2-key',
        MaxCount=1,
        MinCount=1,
        NetworkInterfaces=[{
            'SubnetId': subnet_id,
            'DeviceIndex': 0,
            'AssociatePublicIpAddress': True,
            'Groups': [sg_id]
        }],
        IamInstanceProfile={   # ✅ Add this
            'Name': 'tanujEC2ECRAccessRole'
        },
        UserData=encoded,
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': 'tanujFrontendInstance'}]
        }]
    )
    instance_id = instance['Instances'][0]['InstanceId']
    print(f"✅ Launched Frontend EC2 Instance: {instance_id}")

def main():
    vpc_id = create_vpc()
    subnet_ids = create_subnets(vpc_id)
    igw_id = create_internet_gateway(vpc_id)

    # Create route table and associate with all subnets
    for subnet_id in subnet_ids:
        create_route_table(vpc_id, subnet_id, igw_id)

    sg_id = create_security_group(vpc_id)
    
    # Backend
    backend_lt_id = create_backend_launch_template(sg_id)
    create_asg(backend_lt_id, subnet_ids)  # Pass all subnets to ASG

    # Frontend: just launch in the first subnet (for example)
    launch_frontend_instance(subnet_ids[0], sg_id)


if __name__ == '__main__':
    main()

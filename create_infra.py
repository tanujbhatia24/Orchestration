import boto3

ec2 = boto3.client('ec2')
autoscaling = boto3.client('autoscaling')

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
        AvailabilityZone='us-east-1a')
    subnet_id = subnet['Subnet']['SubnetId']
    print(f"Created Subnet: {subnet_id}")
    return subnet_id

def create_security_group(vpc_id):
    sg = ec2.create_security_group(
        GroupName='WebSG',
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
        LaunchTemplateName='WebAppLT',
        LaunchTemplateData={
            'ImageId': 'ami-0f918f7e67a3323f0',  # replace with your AMI
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
        AutoScalingGroupName='WebAppASG',
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
                'Value': 'WebAppInstance',
                'PropagateAtLaunch': True
            }
        ]
    )
    print("Created Auto Scaling Group")

def main():
    vpc_id = create_vpc()
    subnet_id = create_subnet(vpc_id)
    sg_id = create_security_group(vpc_id)
    launch_template_id = create_launch_template(sg_id)
    create_asg(launch_template_id, subnet_id)

if __name__ == '__main__':
    main()

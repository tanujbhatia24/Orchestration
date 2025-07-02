import boto3
import time

ec2 = boto3.client('ec2')
autoscaling = boto3.client('autoscaling')

ASG_NAME = 'tanujWebAppASG'
LAUNCH_TEMPLATE_NAME = 'tanujWebAppLT'
SECURITY_GROUP_NAME = 'tanujWebSG'

def get_vpc_id_by_sg(sg_name):
    response = ec2.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [sg_name]}])
    if response['SecurityGroups']:
        return response['SecurityGroups'][0]['VpcId']
    return None

def delete_asg():
    try:
        autoscaling.delete_auto_scaling_group(AutoScalingGroupName=ASG_NAME, ForceDelete=True)
        print("✅ Deleted Auto Scaling Group")
    except Exception as e:
        print(f"❌ Error deleting ASG: {e}")

def delete_launch_template():
    try:
        ec2.delete_launch_template(LaunchTemplateName=LAUNCH_TEMPLATE_NAME)
        print("✅ Deleted Launch Template")
    except Exception as e:
        print(f"❌ Error deleting Launch Template: {e}")

def delete_igws(vpc_id):
    igws = ec2.describe_internet_gateways(Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}])
    for igw in igws['InternetGateways']:
        igw_id = igw['InternetGatewayId']
        ec2.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        ec2.delete_internet_gateway(InternetGatewayId=igw_id)
        print(f"✅ Deleted Internet Gateway {igw_id}")

def delete_route_tables(vpc_id):
    rts = ec2.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for rt in rts['RouteTables']:
        assoc_main = any(assoc.get('Main', False) for assoc in rt.get('Associations', []))
        if not assoc_main:
            ec2.delete_route_table(RouteTableId=rt['RouteTableId'])
            print(f"✅ Deleted Route Table {rt['RouteTableId']}")

def delete_subnets(vpc_id):
    subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for subnet in subnets['Subnets']:
        ec2.delete_subnet(SubnetId=subnet['SubnetId'])
        print(f"✅ Deleted Subnet {subnet['SubnetId']}")

def delete_network_interfaces(vpc_id):
    enis = ec2.describe_network_interfaces(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for eni in enis['NetworkInterfaces']:
        try:
            ec2.delete_network_interface(NetworkInterfaceId=eni['NetworkInterfaceId'])
            print(f"✅ Deleted Network Interface {eni['NetworkInterfaceId']}")
        except Exception as e:
            print(f"⚠️ Could not delete ENI {eni['NetworkInterfaceId']}: {e}")

def delete_security_groups(vpc_id):
    sgs = ec2.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for sg in sgs['SecurityGroups']:
        if sg['GroupName'] != 'default':
            try:
                ec2.delete_security_group(GroupId=sg['GroupId'])
                print(f"✅ Deleted Security Group {sg['GroupId']}")
            except Exception as e:
                print(f"❌ Error deleting SG {sg['GroupId']}: {e}")

def delete_vpc(vpc_id):
    try:
        ec2.delete_vpc(VpcId=vpc_id)
        print(f"✅ Deleted VPC {vpc_id}")
    except Exception as e:
        print(f"❌ Error deleting VPC: {e}")

def main():
    print("🔍 Fetching VPC ID from SG...")
    vpc_id = get_vpc_id_by_sg(SECURITY_GROUP_NAME)
    if not vpc_id:
        print("❌ VPC ID not found. Exiting.")
        return

    delete_asg()
    time.sleep(10)  # Ensure ASG is terminated

    delete_launch_template()
    delete_igws(vpc_id)
    delete_route_tables(vpc_id)
    delete_network_interfaces(vpc_id)
    delete_subnets(vpc_id)
    delete_security_groups(vpc_id)
    delete_vpc(vpc_id)

if __name__ == '__main__':
    main()

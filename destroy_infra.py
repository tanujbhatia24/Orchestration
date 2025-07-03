import boto3
import time

ec2 = boto3.client('ec2')
autoscaling = boto3.client('autoscaling')

ASG_NAME = 'tanujbackendASG'
LAUNCH_TEMPLATE_NAME = 'tanujbackendLT'
SECURITY_GROUP_NAME = 'tanujWebSG'
FRONTEND_TAG = 'tanujFrontendInstance'

def get_vpc_id_by_sg(sg_name):
    response = ec2.describe_security_groups(Filters=[{'Name': 'group-name', 'Values': [sg_name]}])
    if response['SecurityGroups']:
        return response['SecurityGroups'][0]['VpcId']
    return None

def get_instance_ids_from_asg(asg_name):
    response = autoscaling.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
    instance_ids = []
    for group in response['AutoScalingGroups']:
        for inst in group['Instances']:
            instance_ids.append(inst['InstanceId'])
    return instance_ids

def get_frontend_instance_ids():
    response = ec2.describe_instances(Filters=[
        {'Name': 'tag:Name', 'Values': [FRONTEND_TAG]},
        {'Name': 'instance-state-name', 'Values': ['pending', 'running', 'stopping', 'stopped']}
    ])
    instance_ids = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])
    return instance_ids

def terminate_instances(instance_ids):
    if instance_ids:
        ec2.terminate_instances(InstanceIds=instance_ids)
        print(f"Terminating EC2 instances: {instance_ids}")
    else:
        print("No EC2 instances found to terminate.")

def wait_for_instance_termination(instance_ids):
    if instance_ids:
        print("Waiting for EC2 instances to terminate...")
        waiter = ec2.get_waiter('instance_terminated')
        waiter.wait(InstanceIds=instance_ids)
        print("All EC2 instances terminated.")
    else:
        print("No EC2 instances to wait for.")

def delete_asg():
    try:
        autoscaling.delete_auto_scaling_group(AutoScalingGroupName=ASG_NAME, ForceDelete=True)
        print("Deleted Auto Scaling Group")
    except Exception as e:
        print(f"Error deleting ASG: {e}")

def delete_launch_template():
    try:
        ec2.delete_launch_template(LaunchTemplateName=LAUNCH_TEMPLATE_NAME)
        print("Deleted Launch Template")
    except Exception as e:
        print(f"Error deleting Launch Template: {e}")

def delete_igws(vpc_id):
    igws = ec2.describe_internet_gateways(Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}])
    for igw in igws['InternetGateways']:
        igw_id = igw['InternetGatewayId']
        ec2.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
        ec2.delete_internet_gateway(InternetGatewayId=igw_id)
        print(f"Deleted Internet Gateway {igw_id}")

def delete_route_tables(vpc_id):
    rts = ec2.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for rt in rts['RouteTables']:
        associations = rt.get('Associations', [])
        is_main = any(assoc.get('Main', False) for assoc in associations)

        # Skip the main route table
        if is_main:
            continue

        # Disassociate all associated subnets first
        for assoc in associations:
            if 'RouteTableAssociationId' in assoc:
                ec2.disassociate_route_table(AssociationId=assoc['RouteTableAssociationId'])

        ec2.delete_route_table(RouteTableId=rt['RouteTableId'])
        print(f"✅ Deleted Route Table {rt['RouteTableId']}")


def delete_subnets(vpc_id):
    subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for subnet in subnets['Subnets']:
        try:
            ec2.delete_subnet(SubnetId=subnet['SubnetId'])
            print(f"Deleted Subnet {subnet['SubnetId']}")
        except Exception as e:
            print(f"Error deleting Subnet {subnet['SubnetId']}: {e}")

def delete_network_interfaces(vpc_id):
    enis = ec2.describe_network_interfaces(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for eni in enis['NetworkInterfaces']:
        try:
            ec2.delete_network_interface(NetworkInterfaceId=eni['NetworkInterfaceId'])
            print(f"Deleted Network Interface {eni['NetworkInterfaceId']}")
        except Exception as e:
            print(f"Could not delete ENI {eni['NetworkInterfaceId']}: {e}")

def delete_security_groups(vpc_id):
    sgs = ec2.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    for sg in sgs['SecurityGroups']:
        if sg['GroupName'] != 'default':
            try:
                ec2.delete_security_group(GroupId=sg['GroupId'])
                print(f"Deleted Security Group {sg['GroupId']}")
            except Exception as e:
                print(f"Error deleting SG {sg['GroupId']}: {e}")

def delete_vpc(vpc_id):
    try:
        ec2.delete_vpc(VpcId=vpc_id)
        print(f"Deleted VPC {vpc_id}")
    except Exception as e:
        print(f"Error deleting VPC: {e}")

def main():
    print("🔍 Fetching VPC ID from SG...")
    vpc_id = get_vpc_id_by_sg(SECURITY_GROUP_NAME)
    if not vpc_id:
        print("VPC ID not found. Exiting.")
        return

    asg_instances = get_instance_ids_from_asg(ASG_NAME)
    frontend_instances = get_frontend_instance_ids()

    # Terminate both frontend EC2 and backend ASG
    delete_asg()
    time.sleep(10)
    terminate_instances(frontend_instances)
    wait_for_instance_termination(asg_instances + frontend_instances)

    # Delete rest of infra
    delete_launch_template()
    delete_igws(vpc_id)
    delete_route_tables(vpc_id)
    delete_network_interfaces(vpc_id)
    delete_subnets(vpc_id)
    delete_security_groups(vpc_id)
    delete_vpc(vpc_id)

if __name__ == '__main__':
    main()

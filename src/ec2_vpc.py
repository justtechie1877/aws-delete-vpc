#!/usr/bin/env python

"""Prerequisite steps:
    1. Check if the vpc_id exists in specified region.
    2. Delete EC2 and RDS instances/clusters.
    If there are running EC2 or RDS instances, you aren't ready to delete VPC.
    Note: This script doesn't remove any VPN or TGW attachments/connections,
    so it'll fail with the error:
    "An error occurred (DependencyViolation) when calling the DeleteVpc
    The vpc 'vpc-xxxxxxxx' has dependencies and cannot be deleted..."

   Remove/destroy steps:
    1. This function is describes and removes all VPC dependencies first
    and then deletes VPC itself. Improved some source code from
    https://github.com/jeffbrl/aws-vpc-destroy/blob/master/vpc_destroy.py
"""

# Standard packages
import logging
import os
import sys
import time

# Third party packages
import boto3
from botocore.exceptions import ClientError

# Sets up logging
logger = logging.getLogger("root")
FORMAT = "[%(filename)s:%(lineno)s ===> %(funcName)8s()]: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)
LOGGER = logging.getLogger("root")
LOGGER.setLevel(logging.DEBUG)


def vpc_exists(vpc_id, aws_region):
    """This function is checking if vpc does exist in specified region.

    :args:
        vpc_id
    :return:
        vpc-id
    """
    session = boto3.Session(
        # aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        # aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        # aws_session_token=os.environ['AWS_SESSION_TOKEN'],
        profile_name=os.environ['AWS_PROFILE'],
        region_name=aws_region
        )
    # Any clients created from this session will use credentials
    # from the [profile_name] section of ~/.aws/credentials.
    ec2_client = session.client('ec2')

    # Check if VpcId does exsist
    try:
        ec2_client.describe_vpcs(VpcIds=[vpc_id])
        return vpc_id
    except ClientError as error:
        LOGGER.error(error)
        LOGGER.info(f"The {vpc_id} doesn't exist in the {aws_region}.")
        sys.exit()


def delete_vpc(vpc_id, aws_region):
    """This function is describes and removes all VPC dependencies first
    and then deletes the VPC itself.

    :args:
        vpc_id, aws_region
    """
    session = boto3.Session(
        # aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        # aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        # aws_session_token=os.environ['AWS_SESSION_TOKEN'],
        profile_name=os.environ['AWS_PROFILE'],
        region_name=aws_region
        )
    # Any clients created from this session will use credentials
    # from the [profile_name] section in ~/.aws/credentials.
    ec2 = session.resource("ec2")
    ec2_client = session.client('ec2')
    vpc = ec2.Vpc(vpc_id)

    # Detach default_dhcp_options if associated with the vpc
    dhcp_options_default = ec2.DhcpOptions("default")
    if dhcp_options_default:
        dhcp_options_default.associate_with_vpc(VpcId=vpc_id)

    # Delete NAT Gateways. Attached ENIs are automatically deleted
    # EIPs are disassociated but not released
    filters = [
        {"Name": "vpc-id", "Values": [vpc_id]}
    ]
    natgws = ec2_client.describe_nat_gateways(Filters=filters)["NatGateways"]
    LOGGER.info(f"The list of NATGW: {natgws}")
    for nat_gw in natgws:
        ec2_client.delete_nat_gateway(NatGatewayId=nat_gw["NatGatewayId"])
        time.sleep(90)

    # Release an IP address without NetworkInterfaceId or AssociationId
    filters = [
        {"Name": "domain", "Values": ["vpc"]}
    ]
    eips = ec2_client.describe_addresses(Filters=filters)['Addresses']
    for eip in eips:
        if 'NetworkInterfaceId' not in eip:
            LOGGER.info(eip['PublicIp'] +
                        " doesn't have any instances associated, releasing")
            ec2_client.release_address(AllocationId=eip['AllocationId'])
        elif 'AssociationId' not in eip:
            LOGGER.info(eip['PublicIp'] +
                        "doesn't have any associationId, releasing")
            ec2_client.release_address(AllocationId=eip['AllocationId'])
            time.sleep(90)

    # Ensure ENIs are deleted before proceeding
    filters = [
        {"Name": "vpc-id", "Values": [vpc_id]}
    ]
    enis = ec2_client.describe_network_interfaces(
        Filters=filters
    )["NetworkInterfaces"]
    for eni in enis:
        LOGGER.info(f"The eni is: {eni}")
        try:
            attachid = eni["Attachment"]["AttachmentId"]
            LOGGER.info(f"The attachId is: {attachid}")
            ec2_client.detach_network_interface(
                AttachmentId=attachid,
            )
            LOGGER.info(f"Detaching {attachid}")
            ec2.delete_network_interface(
                NetworkInterfaceId=eni["NetworkInterfaceId"],
            )
            LOGGER.info(f"Waiting on ENIs to delete")
            time.sleep(30)
        except Exception as ex:
            LOGGER.error(ex)
            if eni not in enis:
                LOGGER.info(f"No ENIs remaining")

    # Detach and delete the IGW associated with the vpc
    igws = vpc.internet_gateways.all()
    for igw in igws:
        vpc.detach_internet_gateway(InternetGatewayId=igw.id)
        LOGGER.info(f"Detaching the IGW ==> {igw.id}")
        igw.delete()

    # Delete the VPC Endpoints
    filters = [
        {"Name": "vpc-id", "Values": [vpc_id]}
    ]
    eps = ec2_client.describe_vpc_endpoints(Filters=filters)["VpcEndpoints"]
    LOGGER.info(f"List of EndPoints: {eps}")
    for ep in eps:
        ec2_client.delete_vpc_endpoints(VpcEndpointIds=[ep["VpcEndpointId"]])

    # Delete custom security groups
    filters = [
        {"Name": "vpc-id", "Values": [vpc_id]}
    ]
    sec_grps = ec2_client.describe_security_groups(
        Filters=filters
    )['SecurityGroups']
    if len(sec_grps) > 0:
        for sg in sec_grps:
            if sg["GroupName"] != "default":
                # LOGGER.info(f'List of SGs_Id: {sg["GroupId"]}')
                for ingress in sg['IpPermissions']:
                    # LOGGER.info(f'List of ingress rules: {ingress}')
                    ec2_client.revoke_security_group_ingress(
                        GroupId=sg["GroupId"],
                        IpPermissions=[ingress],
                    )
                    LOGGER.info(f'Removing {ingress} from Group ID: {sg["GroupId"]},\
                                Group Name: {sg["GroupName"]}'
                                )
                for egress in sg['IpPermissionsEgress']:
                    # LOGGER.info(f'List of egress rules: {egress}')
                    ec2_client.revoke_security_group_egress(
                        IpPermissions=[egress],
                    )
                    LOGGER.info(f'Removing {egress} from Group ID: {sg["GroupId"]},\
                                Group Name: {sg["GroupName"]}'
                                )
                ec2_client.delete_security_group(
                    GroupId=sg['GroupId'],
                )
                LOGGER.info(f'Removing security Group ID {sg["GroupId"]}, \
                        Group Name: {sg["GroupName"]}!')

    # Delete vpc peering connection(s) as vpc-requester
    filters = [
        {"Name": "requester-vpc-info.vpc-id", "Values": [vpc_id]},
    ]
    vpc_peer_conns_req = ec2_client.describe_vpc_peering_connections(
        Filters=filters
    )["VpcPeeringConnections"]
    LOGGER.info(f"VPC-Peer-Conns-req are: {vpc_peer_conns_req}")
    for vpc_peer in vpc_peer_conns_req:
        if vpc_peer["RequesterVpcInfo"]["VpcId"] == vpc_id:
            ec2.VpcPeeringConnection(
                vpc_peer["VpcPeeringConnectionId"]
            ).delete()
            LOGGER.info(f"Deleting peering connection as: \
                        {vpc_peer['VpcPeeringConnectionId']}")
            time.sleep(60)
        else:
            LOGGER.info(f"There is no peering connection as requester...")

    # Delete vpc peering connection(s) as vpc-accepter
    filters = [
        {"Name": "accepter-vpc-info.vpc-id", "Values": [vpc_id]},
    ]
    vpc_peer_conns_acc = ec2_client.describe_vpc_peering_connections(
        Filters=filters
    )["VpcPeeringConnections"]
    LOGGER.info(f"VPC-Peer-Conns-acc are: {vpc_peer_conns_acc}")
    try:
        for vpc_peer_acc in vpc_peer_conns_acc:
            if vpc_peer_acc["AccepterVpcInfo"]["VpcId"] == vpc_id:
                ec2.VpcPeeringConnection(
                    vpc_peer_acc["VpcPeeringConnectionId"]
                ).delete()
                time.sleep(90)
                LOGGER.info(f"Deleting peering connection as: \
                            {vpc_peer_acc['VpcPeeringConnectionId']}")
        else:
            LOGGER.info(f"There is no peering connection as accepter...")
    except ClientError as error:
        logging.error(error)
        pass

    # Detach VPN Gateway
    filters = [
        {"Name": "attachment.state", "Values": ["attached"]},
    ]
    vpn_gws = ec2_client.describe_vpn_gateways(
        Filters=filters
    )["VpnGateways"]
    LOGGER.info(f"List of VPN gateways: {vpn_gws}")
    try:
        for vpn_gw in vpn_gws:
            ec2_client.detach_vpn_gateway(
                    VpnGatewayId=vpn_gw["VpnGatewayId"],
                    VpcId=vpc_id,
            )
            LOGGER.info(f"Detaching the ==> {vpn_gw}")
            time.sleep(60)
    except ClientError as error:
        logging.error(error)
        sys.exit()

    # Detach VPN Gateway. Delete VPN connection.
    # Note - it does not delete VPN Gateway or Customer Gateways
    filters = [
        {"Name": "state", "Values": ["available"]},
        {"Name": "state", "Values": ["attached"]},
    ]
    vpn_conns = ec2_client.describe_vpn_connections(
        Filters=filters
    )["VpnConnections"]
    LOGGER.info(f"List of VPN connections: {vpn_conns}")
    try:
        for vpn_con in vpn_conns:
            if ec2_client.detach_vpn_gateway(
                    VpnGatewayId=vpn_con["VpnGatewayId"],
                    VpcId=vpc_id,
            ):
                ec2_client.delete_vpn_connection(
                    VpnConnectionId=vpn_con["VpnConnectionId"],
                )
                LOGGER.info(f"Deleting the {vpn_con}")
                time.sleep(60)
            elif not ec2_client.detach_vpn_gateway(
                VpcId=vpc_id,
                VpnGatewayId=vpn_con["VpnGatewayId"],
            ):
                LOGGER.info(f"An error occurred (InvalidVpnGatewayAttachment.NotFound) \
                             when calling the DetachVpnGateway operation: \
                             The attachment with vpn gateway ID and \
                             vpc ID {vpc_id} does not exist")
    except ClientError as error:
        logging.error(error)
        sys.exit()

    # Delete transit gateway attachment for this vpc
    # Note - this only handles vpc attachments, not vpn
    filters = [
        {"Name": "vpc-id", "Values": [vpc_id]}
    ]
    tgw_attachments = ec2_client.describe_transit_gateway_vpc_attachments(
        Filters=filters
    )["TransitGatewayVpcAttachments"]
    LOGGER.info(f"List of the TGW attachments: {tgw_attachments}")
    for tgw_attach in tgw_attachments:
        if tgw_attach["VpcId"] == vpc_id:
            ec2_client.delete_transit_gateway_vpc_attachment(
                TransitGatewayAttachmentId=tgw_attach[
                    "TransitGatewayAttachmentId"
                ]
            )
            time.sleep(30)

    # Disassociate the route table(s)
    filters = [
        {"Name": "vpc-id", "Values": [vpc_id]},
        {"Name": "route.state", "Values": ["active"]},
    ]
    route_tables = ec2_client.describe_route_tables(
        Filters=filters
    )["RouteTables"]
    LOGGER.info(f"List of route tables: {route_tables}")
    for route_table in route_tables:
        for association in route_table["Associations"]:
            if not association["Main"]:
                ec2_client.disassociate_route_table(
                    AssociationId=association["RouteTableAssociationId"]
                )
                LOGGER.info(f"Disassotiating the: \
                            {association['RouteTableAssociationId']}"
                            )
                time.sleep(30)

    # Delete subnets
    subnets = ec2_client.describe_subnets(
        Filters=[
            {
                "Name": "vpc-id",
                "Values": [vpc_id]
            },
        ],
    )["Subnets"]
    LOGGER.info(f"List of subnets: {subnets}")
    if len(subnets) > 0:
        for subnet in subnets:
            ec2_client.delete_subnet(SubnetId=subnet["SubnetId"])
            LOGGER.info(f"Deleting subnets ==> {subnet['SubnetId']}")
            time.sleep(10)

    # Delete custom network ACLs
    nacls = ec2.network_acls.all()
    LOGGER.info(f"List of nACLS: {nacls}")
    for netacl in nacls:
        if not netacl.is_default:
            netacl.delete()

    # Delete route(s), route table(s)
    filters = [
        {"Name": "vpc-id", "Values": [vpc_id]},
        {"Name": "route.state", "Values": ["blackhole", "active"]},
    ]
    route_tables = ec2_client.describe_route_tables(
        Filters=filters
    )["RouteTables"]
    LOGGER.info(f"List of route tables: {route_tables}")
    for route_table in route_tables:
        for route in route_table["Routes"]:
            if route["Origin"] == "CreateRoute":
                ec2_client.delete_route(
                    RouteTableId=route_table["RouteTableId"],
                    DestinationCidrBlock=route["DestinationCidrBlock"],
                )
        try:
            ec2_client.delete_route_table(
                RouteTableId=route_table["RouteTableId"]
            )
            LOGGER.info("Deleting route tables")
        except ClientError as error:
            logging.error(error)

    # Delete routing table(s) without subnet associations
    try:
        for route_table in route_tables:
            if route_table["Associations"] == []:
                ec2_client.delete_route_table(
                    RouteTableId=route_table["RouteTableId"]
                )
    except ClientError as error:
        logging.error(error)

    # Finally, delete the vpc
    try:
        ec2_client.delete_vpc(VpcId=vpc_id)
        LOGGER.info(f"Destroying {vpc_id} in {aws_region} !!")
    except ClientError as error:
        logging.error(error)
        LOGGER.error(f"Unable to destroy {vpc_id} in {aws_region}. :(")
        sys.exit()


def main(vpc_id, aws_region):
    vpc_exists(vpc_id, aws_region)
    delete_vpc(vpc_id, aws_region)


if __name__ == "__main__":
    try:
        main(sys.argv[1], sys.argv[2])
    except KeyboardInterrupt:
        exit(0)

#!/usr/bin/env python

"""After deleting a VPC, we've to clean up rest of the "zombie" resources
that were associated/attached to the deleted VPC,
such as VPN connections and VPN Gateway(s).
"""

# Standard Packages
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


def delete_vpn_gw(aws_region):
    """A function to delete any available VPN connectons and
    then deletes VPN Gateway(s).
    
    :args:
        aws_region
    """
    # Set up boto3 session
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

    # Delete VPN connection(s)
    filters = [
        {"Name": "state", "Values": ["available"]},
    ]
    vpn_conns = ec2_client.describe_vpn_connections(
        Filters=filters
    )["VpnConnections"]
    for vpn_con in vpn_conns:
        if 'available' in vpn_con['State']:
            ec2_client.delete_vpn_connection(
                VpnConnectionId=vpn_con["VpnConnectionId"],
                # DryRun = True
            )
            LOGGER.info(f"Deleting the {vpn_con['VpnConnectionId']}")
            time.sleep(60)
        else:
            LOGGER.info(f"The VpnGateway Connection doesn't exist \
                        in the {aws_region} region"
                        )

    # Delete the VPN Gateway(s)
    try:
        vpn_gws = ec2_client.describe_vpn_gateways(
            Filters=[
                {
                    'Name': 'state',
                    'Values': ['available'],
                }
            ]
        )['VpnGateways']
        for vpn_gw in vpn_gws:
            if 'available' in vpn_gw['State']:
                ec2_client.delete_vpn_gateway(
                    VpnGatewayId=vpn_gw['VpnGatewayId'],
                    # DryRun = True
                )
                LOGGER.info(f"Deleting the ==> {vpn_gw['VpnGatewayId']}")
    except ClientError as error:
        LOGGER.error(error)
        LOGGER.error(f"The VGW doesn't exist \
                      in the {aws_region} region."
                     )
        sys.exit()


def main(aws_region):
    """ A main function
    :args:
        aws_region, cust_gw
    """
    delete_vpn_gw(aws_region)


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except KeyboardInterrupt:
        exit(0)

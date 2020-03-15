#!/usr/bin/env python

"""After deleting a VPC, we've to clean up rest of the "zombie" resources
that were associated/attached to the deleted VPC,
such as Customer Gateway.
"""

# Standard Packages
import logging
import os
import sys

# Third party packages
import boto3

# Sets up logging
logger = logging.getLogger("root")
FORMAT = "[%(filename)s:%(lineno)s ===> %(funcName)8s()]: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)
LOGGER = logging.getLogger("root")
LOGGER.setLevel(logging.DEBUG)


def delete_cust_gw(aws_region, cust_gw):
    """ Delete Customer Gateway that had been specified in command line arguments
    
    :args:
        aws_region, cust_gw
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

    # Delete Customer Gateway
    filters = [
        {'Name': 'state', 'Values': ['available'], }
    ]
    cust_gws = ec2_client.describe_customer_gateways(
        Filters=filters
    )['CustomerGateways']
    for cust_gw_id in cust_gws:
        if cust_gw_id['CustomerGatewayId'] == cust_gw:
            ec2_client.delete_customer_gateway(
                CustomerGatewayId=cust_gw_id['CustomerGatewayId'],
                # DryRun = True
            )
            LOGGER.info(f"Deleting the ==> {cust_gw_id['CustomerGatewayId']}")
        else:
            LOGGER.info(f"The {cust_gw_id} doesn't exist in \
                        the {aws_region} region"
                        )


def main(aws_region, cust_gw):
    """ A main function
    
    :args:
        aws_region, cust_gw
    """
    delete_cust_gw(aws_region, cust_gw)


if __name__ == "__main__":
    try:
        main(sys.argv[1], sys.argv[2])
    except KeyboardInterrupt:
        exit(0)

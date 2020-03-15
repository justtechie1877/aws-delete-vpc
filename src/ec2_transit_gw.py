#!/usr/bin/env python

"""After deleting a VPC, we've to clean up rest of the "zombie" recources
that were associated/attached to the deleted VPC,
such as Transit Gateway.
"""

# Standard Packages
import logging
import os
import sys

# Third party packages
import boto3
from botocore.exceptions import ClientError

# Sets up logging
logger = logging.getLogger("root")
FORMAT = "[%(filename)s:%(lineno)s ===> %(funcName)8s()]: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)
LOGGER = logging.getLogger("root")
LOGGER.setLevel(logging.DEBUG)


def delete_tgw(aws_region, tgw_id):
    """ Delete Transit Gateway that had been specified in command line arguments.
    
    :args:
        aws_region, tgw_id
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

    # Delete Transit Gateway
    filters = [
        {'Name': 'state', 'Values': ['available'], }
    ]
    trans_gws = ec2_client.describe_transit_gateways(
        Filters=filters
    )['TransitGateways']
    for trans_gw_id in trans_gws:
        if trans_gw_id['TransitGatewayId'] == tgw_id:
            try:
                ec2_client.delete_transit_gateway(
                    TransitGatewayId=trans_gw_id['TransitGatewayId'],
                    # DryRun=True,
                )
                LOGGER.info(f"Deleting ==> {trans_gw_id['TransitGatewayId']}")
            except ClientError as error:
                logging.error(error)
                sys.exit()
        else:
            LOGGER.info(f"The {trans_gw_id} doesn't exist in \
                        the {aws_region} region"
                        )


def main(aws_region, tgw_id):
    """ A main function
    
    :args:
        aws_region, tgw_id
    """
    delete_tgw(aws_region, tgw_id)


if __name__ == "__main__":
    try:
        main(sys.argv[1], sys.argv[2])
    except KeyboardInterrupt:
        exit(0)

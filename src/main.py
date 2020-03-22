#!/usr/bin/env python

"""Main module execution:
    1. This function parses required/optional command line arguments.
    2. Calls ec2_get_status module
    3. Calls ec2_vpc module 
    4. Calls ec2_vpn_conns_gws module
    5. Calls ec2_customer_gw module
    6. Calls ec2_transit_gw module
    7. Calls ec2_dynamodb_table module
    8. Calls s3_bucket module
"""

# Standard packages
import argparse
import logging
import os
import sys

# Third party packages
from botocore.exceptions import ClientError

# Local imports
import ec2_get_status
import ec2_vpn_conns_gw
import ec2_customer_gw
import ec2_transit_gw
import ec2_dynamodb
import s3_bucket
from ec2_vpc import vpc_exists, delete_vpc

# Sets up logging
logger = logging.getLogger("root")
FORMAT = "[%(filename)s:%(lineno)s ===> %(funcName)8s()]: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)
LOGGER = logging.getLogger("root")
LOGGER.setLevel(logging.DEBUG)


def parse_args(argv):
    """Parse required/optional command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser._action_groups.pop()
    required = parser.add_argument_group("required arguments")
    required.add_argument(
        "--vpc_id", required=True, help="Please include the vpc_id"
    )
    required.add_argument(
        "--region", required=True, help="Please provide the AWS region"
    )

    optional = parser.add_argument_group("optional arguments")
    optional.add_argument(
        "--cust_gw_id", help="The cust_gw_id"
    )
    optional.add_argument(
        "--tgw_id", help="The transit_gw_id"
    )
    
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    # Assign aws_region argument
    if args.region:
        aws_region = args.region
    else:
        try:
            aws_region = os.environ["AWS_DEFAULT_REGION"]
        except KeyError as error:
            logging.error(error)
            LOGGER.info("You must set the environment variable \
                        for the 'AWS_DEFAULT_REGION'")
        sys.exit()

    # Check for the vpc_id in specified region
    try:
        vpc_id = args.vpc_id
        if vpc_exists(vpc_id, aws_region):
            LOGGER.info(f"Found the {vpc_id} in the {aws_region}.\
                         Invoke deletion actions...")
    except ClientError as error:
        logging.error(error)
        sys.exit()

    # Exit clean if there are EC2 or RDS instances in specified vpc_id
    LOGGER.info(f"Calling ec2_get_status...")
    ec2_get_status.main(vpc_id, aws_region)

    # Assign vpc_id argument and run the delete program
    vpc_id = args.vpc_id
    LOGGER.info(f"Calling delete ==> {vpc_id}...")
    delete_vpc(vpc_id=vpc_id, aws_region=aws_region)

    # Delete "zombie" vpn connections and "detached" vpn gateway(s)
    LOGGER.info(f"Calling delete vpn_conns_gws...")
    ec2_vpn_conns_gw.main(aws_region)

    # Assign cust_gw argument and delete the customer gateway
    cust_gw = args.cust_gw_id
    LOGGER.info(f"Calling delete ==> {cust_gw}...")
    ec2_customer_gw.main(aws_region, cust_gw)

    # Delete transit gateway
    tgw_id = args.tgw_id
    LOGGER.info(f"Calling delete ==> {tgw_id}...")
    ec2_transit_gw.main(aws_region, tgw_id)

    # Delete DynamoDB table
    LOGGER.info(f"Calling delete dynamodb...")
    ec2_dynamodb.main(aws_region)

    # Delete S3 bucket
    LOGGER.info(f"Calling delete s3_bucket...")
    s3_bucket.main()
    
#!/usr/bin/env python

"""After deleting a VPC, we've to clean up the rest of the resources
that were created as part of the account creation pipeline such as DynamoDB table.
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


def deleteTable(aws_region):
    """ Delete DynamoDB table that had been created via pipeline
    
    :args:
        aws_region
    """

    # Create boto3 client session
    session = boto3.Session(
        # aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        # aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        # aws_session_token=os.environ['AWS_SESSION_TOKEN'],
        profile_name=os.environ['AWS_PROFILE'],
        region_name=aws_region
    )
    # Any clients created from this session will use credentials
    # from the [profile_name] section of ~/.aws/credentials.
    dynamodb_client = session.client('dynamodb')

    # Delete DynamoDB table(s)
    ddb_tables = dynamodb_client.list_tables()['TableNames']
    try:
        if ddb_tables != []:
            for ddb in ddb_tables:
                dynamodb_client.delete_table(
                    TableName=ddb
                )
                LOGGER.info(f"Deleting the ==> {ddb}")
        else:               
            LOGGER.info(f"The DynamoDB table doesn't exist in \
                        the {aws_region} region"
                        )
    except ClientError as error:
        LOGGER.error(error)


def main(aws_region):
    """ A main function
    
    :args:
        aws_region
    """
    deleteTable(aws_region)


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except KeyboardInterrupt:
        exit(0)

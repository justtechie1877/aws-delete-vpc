#!/usr/bin/env python

"""After deleting a VPC, we've to clean up the rest of the resources
that were created as part of the account creation pipeline such as S3 bucket.
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


def delete_s3_bucket():
    """ Delete S3 bucket that had been created via account creation pipeline
    
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
    )
    s3_client = session.client('s3')
    s3 = session.resource('s3')

    # List the bucket(s)
    s3_buckets = s3_client.list_buckets()['Buckets']
    LOGGER.info(f"List of buckets ==> {s3_buckets}")
    try:
        if s3_buckets != []:
            for bucket in s3_buckets:
                s3_bucket = s3.Bucket(bucket['Name'])

                # Delete all object versions
                s3_bucket.object_versions.all().delete()
                
                # Delete S3 bucket
                s3_client.delete_bucket(
                    Bucket=bucket['Name']
                )
                LOGGER.info(f"Deleting the ==> {bucket['Name']}")
        else:                
            LOGGER.info(f"The S3 bucket(s) doesn't exists.")
         
    except ClientError as error:
        LOGGER.error(error)
    
   
def main():
    """ A main function

    """
    delete_s3_bucket()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit(0)
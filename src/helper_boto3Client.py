#!/usr/bin/env python

"""A helper function to initialize a boto3 client. 
"""

# Standard Packages
import logging
import os
import sys

# Third party packages
import boto3
from botocore.exceptions import ClientError
from boto3.session import Session

# Sets up logging
logger = logging.getLogger("root")
FORMAT = "[%(filename)s:%(lineno)s ===> %(funcName)8s()]: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)
LOGGER = logging.getLogger("root")
LOGGER.setLevel(logging.DEBUG)


def init_boto_client(aws_region, client_name='ec2'):
    """Initiates boto's client object.
    
    :param aws_region: region
    :param client_name: client name ==> set 'ec2' as default
    :return: boto_client
    """
    aws_session_token=['']
    profile=['']
    if aws_session_token != ['']:
        session = boto3.session.Session(
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
            aws_session_token=os.environ['AWS_SESSION_TOKEN'],
            region_name=os.environ['AWS_DEFAULT_REGION']
        )
        boto_client = session.client(client_name)
    elif profile != ['']:
        session = boto3.session.Session(
            profile_name=os.environ['AWS_PROFILE'],
            region_name=aws_region
        )
        boto_client = session.client(client_name)
    else:
        boto_client = boto3.client(
            client_name, 
            region_name=aws_region
        )
    return boto_client 


if __name__ == "__main__":
    try:
        init_boto_client(sys.argv[1], client_name='ec2')
        #ec2_client=init_boto_client(sys.argv[1], client_name='ec2')
        #LOGGER.info(f"ex2 client {ec2_client}")
    except KeyboardInterrupt:
        sys.exit(0)  


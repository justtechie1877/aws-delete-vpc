#!/usr/bin/env python

"""  AWS EC2 and RDS DB status check
This module checks for the EC2 instance(s) and RDS DB instance(s)/cluster(s)
status for the specified VPC in the particular region.

TODO:
    - The get_rds_status function under development
"""

# Standard Packages
import os
import sys
import logging
# from tabulate import tabulate

# None Standard packages
import boto3

print("AWS_PROFILE is: " + os.environ['AWS_PROFILE'])

# Sets up logging
logger = logging.getLogger("root")
FORMAT = "[%(filename)s:%(lineno)s ===> %(funcName)8s()]: %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)
LOGGER = logging.getLogger("root")
LOGGER.setLevel(logging.DEBUG)


def get_ec2_status(vpc_id, aws_region):
    """A function to describe the EC2 instance resources.
    Args:
    vpc_id, aws_region
    Returns:
    True statement ==> clean exit if there are some running instances
    """

    # Create a boto3 session profile
    session = boto3.Session(
        # aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        # aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        # aws_session_token=os.environ['AWS_SESSION_TOKEN'],
        profile_name=os.environ['AWS_PROFILE'],
        region_name=aws_region
        )
    # Any clients created from this session will use credentials
    # from the [profile_name] section of ~/.aws/credentials.
    ec2client = session.client('ec2')

    # Check for running EC2 instance(s)
    filters = [
        {"Name": "instance-state-name", "Values": ["running", "stopped"]},
        {"Name": "vpc-id", "Values": [vpc_id]},
    ]
    ec2_instances = ec2client.describe_instances(
        Filters=filters
    )['Reservations']
    instance_ids, state_names = [], []
    if len(ec2_instances) > 0:
        for res in ec2_instances:
            for ins in res['Instances']:
                instance_ids.append(ins['InstanceId'])
                inst_id = ''.join(instance_ids)
            # instance_ids = ''.join(instance_ids.append(ins['InstanceId']))
                state_names.append(ins['State']['Name'])
                st_name = ''.join(state_names)
            # state_names = ''.join(state_names.append(ins['State']['Name']))
                # return inst_id
            # LOGGER.info(f"Running EC2 {inst_id} with status: \
            # <{st_name}> in the {vpc_id}.")
            # print(tabulate([{inst_id}], [{st_name}], headers=['instance_ids',
            # 'state_names'])
            # )
        sys.exit(f"Running EC2 {inst_id} with status: <{st_name}> in the {vpc_id}. \
                 Please delete the EC2 or RDS instance/cluster first..."
                 )
    else:
        LOGGER.info(f"No running EC2 instances in the {vpc_id}.")


def get_rds_status(vpc_id, aws_region):
    """A function to describe the RDS DB instance resources.
    Returns:
    True statement
    """
    # Create a boto3 session profile
    session = boto3.Session(
        # aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        # aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        # aws_session_token=os.environ['AWS_SESSION_TOKEN'],
        profile_name=os.environ['AWS_PROFILE'],
        region_name=aws_region
        )
    # Any clients created from this session will use credentials
    # from the [profile_name] section of ~/.aws/credentials.
    rds = session.client('rds')

    # Check for RDS instances
    filters = [
        {"Name": "db-instance-id", "Values": ["available"]},
        # {"Name": "tag:Name", "Values": [vpc_id]},
    ]
    rds_instances = rds.describe_db_instances(Filters=filters)['DBInstances']
    if len(rds_instances) > 0:
        for rdb in rds_instances:
            if rdb["DBSecurityGroup"]["VpcId"] == vpc_id:
                LOGGER.info(
                    f"Running RDS instances/clusters exist in {vpc_id}."
                )
    else:
        LOGGER.info(f"No running RDS DB instances in {vpc_id}.")


def main(vpc_id, aws_region):
    get_ec2_status(vpc_id, aws_region)
    get_rds_status(vpc_id, aws_region)


if __name__ == "__main__":
    try:
        main(sys.argv[1], sys.argv[2])
    except KeyboardInterrupt:
        exit(0)

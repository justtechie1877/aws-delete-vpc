# AWS VPC Deletion Service

## Overview

This repository contains Python boto3 scripts for the AWS VPC tear down with it's dependencies and other resources such as VPN connection(s), VPN Gateway(s), 
Internet Gateway, Customer Gateway, DyanmoDB and S3 bucket.

!!! Word of Warning !!! - Please consider runnig these scripts against AWS acount that deemed for closure/decommission request ONLY.

# Content

* [Program Usage](#program-usage)
* [Design](#design) - TBA
* [Repository Contents](#repository-contents)
      * [Python Modules](#python-modules)
* [Dependencies](#dependencies)
* [Testing](#testing)
* [Changelog](#changelog)
* [Contributing](#contributing)

<a name="program-usage"></a>

## Program Usage

```
$ ./main.py -h

usage: main.py [-h] --vpc_id VPC_ID [--cust_gw_id CUST_GW_ID]
               [--region REGION]

required arguments:
  --vpc_id VPC_ID       Please include the vpc_id
  --region REGION       Please provide the AWS region

optional arguments:
  --cust_gw_id CUST_GW_ID
                        The cust_gw_id
  --tgw_id TGW_ID       The transit_gw_id


### Sample Output
[ec2_vpc.py:350 ===> delete_vpc()]: Destroying vpc-xxxxxxxxxxxxxx in eu-west-2 !!
[main.py:104 ===> <module>()]: Calling delete_vpn_conns_gws...
[credentials.py:1196 ===>     load()]: Found credentials in shared credentials file: ~/.aws/credentials
[ec2_vpn_conns_gws.py:78 ===> delete_vpn_gw()]: Deleting the ==> vgw-xxxxxxxxxxxxxx
[credentials.py:1196 ===>     load()]: Found credentials in shared credentials file: ~/.aws/credentials
[ec2_vpn_conns_gws.py:114 ===> delete_cust_gw()]: Deleting the ==> cgw-xxxxxxxxxxxxxx

```

<a name="design"></a>

## Design ==> TBA

| Type | Link |
|--------|---------|
| Design Diagram | [AWS VPC deletion](images/aws-vpc-delete-service.png) |  ==> TBA

<a name="repository-contents"></a>

## Repository Contents



<a name="python-modules"></a>

### Python Modules

There are multiple Python modules that facilitate the AWS VPC deletion.

<a name="dependencies"></a>

## Requirements and Dependencies

### AWS Account IAM Role

The AWS Account IAM role is the role that the user/service account/Lambda function assumes in order to run the program for the particular account.
In order to create a boto3 session profile, you need to run the following commands:
```
export AWS_PROFILE="profile_name"
export AWS_DEFAULT_REGION'="region"  
                       OR
export AWS_ACCESS_KEY_ID="<aws_key_id>"
export AWS_SECRET_ACCESS_KEY="<aws_secret_access_key>"
export AWS_SESSION_TOKEN="<aws_session_token>"
```

<a name="testing"></a>

## Testing

There is a Makefile that is configured to perform:
    - flake8 on python scripts
        - ```Make flake8-python```

<a name="changelog"></a>

## Changelog

For a summary of version releases of this repository, please see the [CHANGELOG](CHANGELOG.md).

<a name="contributing"></a>

## Contributing

To contribute, please see the [CONTRIBUTING](CONTRIBUTING.md) file.
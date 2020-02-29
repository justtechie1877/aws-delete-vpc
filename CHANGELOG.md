# Delete AWS resources CHANGELOG


## Major Release 1.0.0

- Created Python scripts:

    1) Checks for the EC2 instance(s) status for the specified VPC in the particular region.

    2) Describes and removes all VPC dependencies first and then deletes VPC itself.

    3) Clean up rest of the "zombie" recources that were associated/attached to the deleted VPC.


## Minor Release 1.1.0

- Updated CONTRIBUTING to better reflect Gitflow

- Updated README with recommended content


## Hotfix Release
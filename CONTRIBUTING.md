# Contributing

This repository makes use of __Git Flow__. When contributing to this repository, please ensure that you follow the appropriate __Git Flow Process__ as defined below.

For additional information please see: [Atlassian - Gitflow Workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)


## Versioning

This repository makes use of [Semantic Versioning](https://semver.org/).

Core concept being ```MAJOR.MINOR.PATCH```


## Standards and Ways of Working

* Merge frequently, it is much easier and quicker for people to review concise code

* Lint your code before you commit

* Communicate with others working on the same repository

* Clearly document nuances and edge cases of the code within the repository, essentially anything that isn't self explanatory within the code.



## Pull Request Process

### Feature Pull Request Process

#### Pull Request to Develop

1. Pull from the develop branch and resolve any issues or conflicts

2. Create a "feature" branch (e.g. feature/delete-vpn-conns) from develop branch

3. Update the README where neccesary

4. Raise a pull request to the develop branch

5. Ensure that your pull request is reviewed by at least two people

6. Resolve any issues raised during the pull request review

7. Merge to the develop branch and ensure that you delete your feature branch 


#### Release Pull Request to Master

1. Create a "release" branch (e.g. release/1.0.0) from develop branch

2. Pull from the master branch and resolve any issues and/or conflicts

3. Update the CHANGELOG

4. Create a pull request to the master branch

5. Ensure that your pull request is reviewed by at least two people

6. Resolve any issues raised during the pull request review

7. Merge to the master branch

8. Tag the master branch with the new release version


### Hotfix Pull Request Process

1. Create a "hotfix" branch (e.g. hotfix/fix-route-tables) from the master branch

2. Update the README where neccesary

3. Update the CHANGELOG

4. Pull from the master branch and resolve any issues and/or conflicts

5. Create a pull request to the master branch

6. Ensure that your pull request is reviewed by at least two people

7. Reolve any issues raised during the pull request review

8. Merge to the master branch

9. Tag the master branch with the new release version
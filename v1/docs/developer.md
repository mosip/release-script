# Developer docs

Release script contains multiple stages:
* clean
* verify_branch
* checkout
* dependency_check
* dependency_update
* build
* trigger_update
* commit
* push

_* All the stages mentioned above are in execution sequence_

## Clean

* Deletes the checked out repos 
* Deletes generated data during execution
* Deletes the maven local repo jar related to mosip

Command: `python3 main.py clean`

## Verify branch

Checks if the branch exists in the mentioned repository (listed in repoList.json)

Command: `python3 main.py verify_branch`

Output: _generatedData/branchVerification.json_

In output, you can check which repos doesn't contains the target branch

## Checkout

It will checkout all repositories provided in repoList.json which contains the target branch

Command: `python3 main.py checkout`

Requires:
* verify_branch

Output: _generatedData/checkout.json_

## Dependency check

Check if the repository poms contains any outdated MOSIP dependency.

Command: `python3 main.py dependency_check`

Requires:
* checkout

Output: 
* _generatedData/dependencyCheck.json_
* _generatedData/dependencyCheckDetailed.json_

From the above outputs, you can check the information regarding the outdated dependencies 

## Dependency update

Updates the outdated dependencies with the release name

Command: `python3 main.py dependency_update`

Requires:
* checkout

Output: 
* _generatedData/dependencyUpdate.json_

## Build

Build the repo

Command: `python3 main.py build`

Requires:
* checkout

## Trigger update

Update the release repo of the push trigger

Command: `python3 main.py trigger_update --release`

Requires:
* checkout

## Commit

Commit the changes with a commit message

Command: `python3 main.py commit`

Requires:
* checkout

## Push

Push the changes to remote repository

Command: `python3 main.py push`

Requires:
* checkout

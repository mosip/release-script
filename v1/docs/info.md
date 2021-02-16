# Release script v1 info

## Inputs to script

Inputs: branch name, release name

## Actions

### Cleanup

Clean the script generated data

### Checkout

Checkout the repos in the repo folder

### 
Action #1: Fetch list of repos
Get the list of repo in the organization MOSIP
https://gist.github.com/ControlledChaos/418a6e03be1a51d6d81fccb1c141ad7b and save it to action1.response.json

Action #2: Checkout all repo with as input branch
Checkout all repos listed in action1.response.json to the given input branch

Action #3: Branch verification
Inform all the repo's (listed in action1.response.json) that do not have the input branch. 

Action #4: Find and report all projects that have older dependencies
Find and report all projects (listed in action1.response.json) that have older dependencies
Note: If i want to just run only this i should be able to run.
** Ways to find whether a project have older dependency?

Action #5: Set the push trigger
Set the push trigger to use RELEASE_URL instead of OSSRH_SNAPSHOT_URL
** more info about this step

Action #6: Update pom.xml with correct version
Modify all the pom.xml to have the correct version and upto date dependencies.

Action #7: Attempt a clean build
Attempt a clean build and ensure its working.
Note: for every repo delete the local .m2 folder

Action #8: Git commit
Perform git add and git commit with the a comment that its performed by the release script for the release of <release name>

Action #9:
Push the change.

Action #10
Monitor the build action.

Action #11
Relase from nexus repo
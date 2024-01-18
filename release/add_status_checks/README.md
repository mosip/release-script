# Overview
This GitHub Action is designed to help you enable status checks that must pass before allowing merges into specific branches. By utilizing the provided CSV file and API methods (Add, Delete, Get), you can dynamically manage the required status checks on your repository branches.

## Run manual workflow
The action is triggered through a workflow dispatch event, allowing you to specify the API method (Add, Get, Delete) and providing the necessary parameters via inputs.

## checks.csv
*Provide the GitHub username and repository name in the REPO section and specify the branch in the BRANCH section.
### Checks can be added using the following methods in the checks.csv :
* Obtain the push-trigger job name and the Kattu job name, for example: build-commons/maven-build.

* If using a matrix in the job, obtain the name(servicename) of the job and the Kattu job name, for example: kernel-idgenerator-service / build-dockers.

* Alternatively, simply run the dummy pull_request to get the required checks and add them in checks.
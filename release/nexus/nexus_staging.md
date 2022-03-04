## NEXUS repository manager
1. Login to Nexus and verify if all the artifacts to be released from respective repos are there in staging repository in closed state without any validation failure.
1. If any artifactory repo is in open state do select the same and close it and wait for sucessful closing of the repos there. 
1. If repos don't close sucessfully note the validation failures there nd make the required changes in the POM files in the repository and commit the changes. 
1. After artifactory repositories sucessful closing from the staging repository in NEXUS do crosscheck if the version to be released for each artifacts is already not released in Maven central. 
1. Once after ensuring that the version to be released is unique and is not present already in Maven Central release the repositories from NEXUS. 
1. Wait until the arifactories released are shown under specified version in Maven central.
1. Trigger the release changes for the other dependent repos in sequence.

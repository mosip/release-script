# NEXUS repository manager

## Overview
* NEXUS is a repository manager
* It allows you to proxy, collect, and manage your dependencies so that you are not constantly juggling a collection of JARs
* It makes it easy to distribute your software. Internally, you configure your build to publish artifacts to Nexus and they then become available to other developers.
* In MOSIP once after QA testing round is over, we use NEXUS as a mediun to collect all the releasable Jar's and packages created as part of sucessfull github action executions.
* Once Jars and packages reaches the `staging repository` of NEXUS, as per the requirement we move them to `Maven Central Repository` or discard as per the need.
* The `NEXUS staging repository` ensures that we are not directly pushing all the artifacts to the Maven Central without checking the specific versions.   

## Release Artifacts to Maven Central Repo
1. We should follow the [sequence](../docs/repo-sequence.md) for releasing the artifacts to the Maven Central Repository.
1. Login to Nexus and verify if all the artifacts to be released from respective repos are there in staging repository in closed state without any validation failure.
    1. If any artifactory repo is in open state then do select the same, close it manually and wait for sucessful closing of the repos there. 
    1. If repos don't close sucessfully, note the validation failures there and make the required changes in the POM files in the repository and commit the changes.
    1. Also delete the non closed artifactory repo after noting the validation failures.  
1. After artifactory repositories sucessful closing from the staging repository in NEXUS do crosscheck if the version to be released for each artifacts is already not released in Maven central. 
1. Once after ensuring that the version to be released is unique and is not present already in Maven Central **Release** the repositories from NEXUS. 
1. Wait until the arifactories released are shown under specified version in Maven central.
1. Trigger the release changes for the other dependent repos in [sequence](../docs/repo-sequence.md).

# MOSIP Release Preparation

## Overview
Use this guide to release specific MOSIP version.

## Pre-requisites
* All the pre-requisites are mentioned in [pre-requisites guide](docs/pre-requisites.md).
* Make sure proper branching rules are followed. For more details see [MOSIP repo Branching Rules](docs/branching-strategies.md).
## Steps
1. Create release-branch from the release-candidate branch and name it as below:
    ```
    release-<release-version>
    eg: release-1.2.0
    ```
1. After the release-branch is created from release-candidate branch make sure all the changes are merged to develop branch also.
1. Execute the `release_changes` mannual github action from release branch for release preparation.
1. Review and merge the pull request created by release bot from release-branch. While reviewing keep note of the below mentioned points:
    * It should contain the latest POM version changes throughout all the POM's.
    * Change in artifacts publish URL from `OSSRH_SNAPSHOT_URL` to `RELEASE_URL`.
    * It should remove the `-DskipTests` references from all the triggers so that tests are not skipped while building and release and analysis.
    * If PR contains changes in Dockerfile for changing `libs-snapshot-local` reference to `libs-release-local`.
        * If this instance is found in the Dockerfile, update the same to `artifactory-ref-impl` repo owner so that it can be handled in the artifactory docker image as well
1. Once PR is merged, wait for the sucessfull completion of actions. If not sucessfull resolve the issue and make it sucessfull.
1. After successful action run, go to Nexus Repository Manager and release the artifacts to maven central as per [nexus_staging_guide](nexus/nexux-staging.md).
1. After successfull release of artifacts to Maven Central for all the repositories move the docker images from  `mosipdev` organisation created as part of release to `mosipid` organisation using [push scripts guide](vidivi/README.md)
1. After the imges are moved to `mosipid` initiate [signing](Signing/README.md) of all the docker images.
1. Update the `master` branch of all the Modular repositories as per [master update strategy](strategies/master-updates.md).
1. Tag all the repos release branch.
1. Change the branching rules to lock the branch for any further changes until next planned release.
1. Release check shall be performed as per [Release checks](docs/release-check.md).

## GitHub manual workflow to transfer images
Steps to run transfer images from one docker hub account to another.
* Update the docker images list in the images.txt file and commit it.
* Go to Actions, in all workflows we have a manual workflow named `manual workflow to transfer images.
* Select that manual workflow to transfer images, and then click on Run workflow.
* while running manual workflow it will ask for workflow inputs as below .
  1. branch: select specific branch
  1. username: username of the destination dockerhub account
  1. token: password/token of the destination dockerhub account.
  1. destination_organisation: destination dockerhub organisation.
* Next click on `run workflow`.

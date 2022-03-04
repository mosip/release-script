# MOSIP Release Preparation

Below mentioned are the steps taken in an order For MOSIP release:

1. Check if all the [pre-requisites](docs/release_pre-requisites.md) are there to start for the release.
1. Release branches must be locked and no direct merge permission should be there without involving the build and release team even for repository admins once release is announced.
1. Create release-branch from the release-candidate branch and name it as:
    ```
    release-<release-version>
    eg: release-1.2.0
    ```
1. Execute the release_changes mannual action for release preparation.
1. Review and merge the pull request created by release bot from release-branch. While reviewing keep note of the below mentioned points:
    * It should contain the latest release  version changes throughout all the POM's.
    * Change in artifacts publish URL from `OSSRH_SNAPSHOT_URL` to `RELEASE_URL`.
    * It should remove the `-DskipTests` references from all the triggers so that tests are not skipped while building and release and analysis.
    * If PR contains changes in Dockerfile for changing `libs-snapshot-local` reference to `libs-release-local` .
1. Once PR is merged wait for the sucessfull completion of actions. If not sucessfull resolve the issue and make it sucessfull.
1. After successful action run go to Nexus Repository Manager and release the artifacts to maven central as per [nexus_staging_guide](nexus/nexux_staging.md)
1. After successfull release of artifacts to Maven Central for all the repositories move the images from  `mosipdev` organisation created as part of release to `mosipid` organisation using [push scripts guide](vidivi/README.md)
1. After the imges are moved to `mosipid` initiate [signing](image-sign/README.md) of all the docker images.
1. Release check shall be performed as [here](docs/release-check.md)

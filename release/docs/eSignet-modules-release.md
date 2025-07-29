## Overview
Use this guide to release eSignet, Signup, and eSignet-plugins version.

## Pre-requisites
* All the pre-requisites are mentioned in [pre-requisites guide](pre-requisites.md).
* Ensure proper branching rules are followed. For more details see [MOSIP repo Branching Rules](branching-rule.md).

## Release Steps for eSignet
1. Create `release-branch` from the release-candidate branch and name it as follows:
    ```
    release-<release-version>
    eg: release-1.3.x
    ```

2. Ensure that the `pom.xml` files should be updated with the release version of SNAPSHOT release branch ( Ex. release-1.3.x ). 
   * If not, please coordinate with the developer to ensure it is updated.

3. Ensure that the `db_upgrade` and `db_rollback` scripts are updated with the latest release version.
   * If not, coordinate with the developer to make the necessary updates.

4. Execute the ```Release/Pre-release Preparation``` by running the [Action](https://github.com/mosip/release-script/actions/workflows/release-changes.yml).
    * Below inputs for `Release/Pre-release Preparation`
      * Repo URL ( e.g., mosip/< repo name > )
      * Repo Branch  ( e.g., release-1.3.x )
      * tag to update ( update release version Ex. 1.3.0 )
      *  tag to be replaced ( replace SNAPSHOT version Ex. 1.3.0-SNAPSHOT )
      *  base branch for PR ( e.g., release-1.3.x )
      *  Next click on ```run workflow```

5. Ensure that the `pom.xml` files are updated with the correct dependency versions for **esignet-mock-plugin, mosip-identity-plugin, sunbird-rc-plugin, and mock-plugin**, ensuring that the release versions for the dependencies are not identical.

6. Review and merge the pull request created by release bot from `releas-branch` to the respective release repository. While reviewing, ensure the following:
    * Ensure that the latest POM version updates are reflected across all POM files.
    * Ensure that there are no SNAPSHOT versions in the Pull Request or the respective release branch.
    * It should remove the `-DskipTests` references from all the triggers so that tests are not skipped while building and release and analysis.
    * If PR contains changes in Dockerfile for changing `libs-snapshot-local` reference to `libs-release-local`.
        * If this instance is found in the Dockerfile, update the same to `artifactory-ref-impl` repo owner so that it can be handled in the artifactory docker image as well.

7. After all changes are merged into the release branch, wait for the GitHub Actions workflow to complete, which includes the following builds:
    * Maven Build
    * Docker Build
    * Publish to Nexus Build
    * Sonar Analysis Build
    * The `build_maven_esignet_with_plugins` build will fail and needs to be disregarded.

8. Log in to [Central](https://central.sonatype.com/) to release the artifacts to Maven Central.
    * Ensure that all artifacts are in a closed state in the Central staging repository
    * Ensure that all artifact versions match the release version.
    * Click on `Release` Staging Repositories to release the artifacts to Maven Central.
9. Perform the **esignet, apitest-esignet and oidc-ui** docker images transfer from `mosipdev` to `mosipid` using the release version from [here](../vidivi/README.md)
    * Ensure that the Docker/Image tag is updated correctly with the release version.

10. Verify that the released artifacts are present on [Maven central](https://repo1.maven.org/maven2/io/mosip/)

11. Kindly update the [base image of the esignet-with-plugins Dockerfile](https://github.com/mosip/esignet/blob/master/esignet-with-plugins/Dockerfile#L1) from the eSignet release branch to reference the latest transferred eSignet image and get pull request merge.

12. Run [Manual Workflow](https://github.com/mosip/esignet/actions/workflows/manual-docker-build.yml) to build the esignet-with-plugins docker image.

13. Perform the esignet-with-plugins docker image transfer from `mosipdev` to `mosipid` using the release version from [here](../vidivi/README.md)

14. Execute the ```Helm-release Preparation``` by running the [Action](https://github.com/mosip/release-script/actions/workflows/helm-release.yaml)
    * Below inputs for `Helm-release Preparation`
        * Repo URL ( e.g., mosip/< repo name > )
        * Repo Branch  ( e.g., release-1.3.x )
        * Versions for Chart.yaml and install.sh files, format: CHART_VERSION,INSTALL_CHART_VERSION ( 1.3.0-beta.1 )
        * Tag to update in values.yaml ( 1.3.0-beta.1 )
        * base branch for PR ( e.g., release-1.3.x )
        * commit message ( DSD no. )
        * Next click on ```run workflow```
15. Ensure that the Helm `Chart.yaml` is updated with the release version, and modify `install.sh` accordingly. Additionally, update `values.yaml` with the latest released Docker image version.

16. After all changes are merged into the release branch, wait for the `Helm Chart Publish` GitHub Actions to complete.

17. Create a `DSD/MOSIP` ticket for image signing by the Security team.

18. Tag the respective release repositories with the release version as outlined in the [documentation](../gh_release/README.md)

19. Merge the release code into the master branch from [master update strategy](../strategies/master-updates.md)

20. Change the branching rules to lock the branch for any further changes until next planned release.

21. Release check shall be performed as per [Release checks](release-check.md).

## Release Steps for eSignet-Signup
* Please follow the steps outlined above, from Step 1 through Step 6, as part of the process.

7. After all changes are merged into the release branch, wait for the GitHub Actions workflow to complete, which includes the following builds:
    * Maven Build
    * Docker Build
    * Publish to Nexus Build
    * Sonar Analysis Build
    * The `build_maven_signup_with_plugins` build will fail and needs to be disregarded.

8. Log in to [Central](https://central.sonatype.com/) to release the artifacts to Maven Central.
    * Ensure that all artifacts are in a closed state in the Central staging repository
    * Ensure that all artifact versions match the release version.
    * Click on `Release` Staging Repositories to release the artifacts to Maven Central.

9. Perform the **signup-service, apitest-signup and signup-ui** docker images transfer from `mosipdev` to `mosipid` using the release version from [here](../vidivi/README.md)
    * Ensure that the Docker/Image tag is updated correctly with the release version.

10. Verify that the released artifacts are present on [Maven central](https://repo1.maven.org/maven2/io/mosip/)

11. Kindly update the [base image of the signup-with-plugins Dockerfile](https://github.com/mosip/esignet-signup/blob/master/signup-with-plugins/Dockerfile#L1) from the eSignet release branch to reference the latest transferred eSignet image and get pull request merge.

12. Run [Manual Workflow](https://github.com/mosip/esignet-signup/actions/workflows/manual-docker-build.yml) to build the esignet-with-plugins docker image.

13. Perform the signup-with-plugins docker image transfer from `mosipdev` to `mosipid` using the release version from [here](../vidivi/README.md)

Please follow the steps outlined above, from Step 14 through Step 21, as part of the process.

# eSignet modules Post Release Process
* For post release process follow from [here](../../release/README.md)

# GitHub manual workflow to images transfer
* Please refer to Image transfer from [here](../vidivi/README.md)

# Tagging of Repos Workflow
* Please refer to the Tagging of Repos link to [here](../gh_release/README.md)

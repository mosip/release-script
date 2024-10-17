# MOSIP Release Process

## Overview
Use this guide to release specific MOSIP version.

## Pre-requisites
* All the pre-requisites are mentioned in [pre-requisites guide](docs/pre-requisites.md).
* Ensure proper branching rules are followed. For more details see [MOSIP repo Branching Rules](docs/branching-rule.md).
## Steps
1. Create `release-branch` from the release-candidate branch and name it as follows:
    ```
    release-<release-version>
    eg: release-1.3.x
    ```
1. Ensure that the `pom.xml` files should be updated with the release version of SNAPSHOT in the release branch ( Ex. release-1.3.x ).
    * If not, please coordinate with the developer to ensure it is updated.
1. Ensure that the `db_upgrade` and `db_rollback` scripts are updated with the latest release version.
    * If not, coordinate with the developer to make the necessary updates.
1. Execute the ```Release/Pre-release Preparation``` by running the [Action](https://github.com/mosip/release-script/actions/workflows/release-changes.yml).
    * Below inputs for `Release/Pre-release Preparation`
      1. Repo URL ( e.g., mosip/< repo name > )
      1. Repo Branch  ( e.g., release-1.3.x )
      1. tag to update ( update release version Ex. 1.3.0 )
      1. tag to be replaced ( replace SNAPSHOT version Ex. 1.3.0-SNAPSHOT )
      1. base branch for PR ( e.g., release-1.3.x )
      1. Next click on ```run workflow```
1. Review and merge the pull request created by release bot from `releas-branch` to the respective release repository. While reviewing, ensure the following:
    * Ensure that the latest POM version updates are reflected across all POM files.
    * Ensure that there are no SNAPSHOT versions in the Pull Request or the respective release branch.
    * It should remove the `-DskipTests` references from all the triggers so that tests are not skipped while building and release and analysis.
    * If PR contains changes in Dockerfile for changing `libs-snapshot-local` reference to `libs-release-local`.
      1. If this instance is found in the Dockerfile, update the same to `artifactory-ref-impl` repo owner so that it can be handled in the artifactory docker image as well
      1. Ensure that the Helm `Chart.yaml` is updated with the release version, and modify `install.sh` accordingly. Additionally, update `values.yaml` with the latest released Docker image version.
1. After all changes are merged into the release branch, wait for the GitHub Actions workflow to complete, which includes the following builds:
    * Maven Build
    * Docker Build
    * Publish to Nexus
    * Sonar Analysis
    * Helm Chart Publish
1. Log in to [Nexus](https://oss.sonatype.org/#welcome) to release the artifacts to Maven Central.
    * Ensure that all artifacts are in a closed state in the Nexus staging repository
    * Ensure that all artifact versions match the release version.
    * Click on `Release` Staging Repositories to release the artifacts to Maven Central.
1. Verify that the released artifacts are present on [Maven central](https://repo1.maven.org/maven2/io/mosip/)
1. Perform the image transfer from `mosipdev` to `mosipid` using the release version from [here](vidivi/README.md)
    * Ensure that the Docker tag is updated correctly with the release version.
1. Create a `DSD/MOSIP` ticket for image signing by the Security team.
1. Tag the respective release repositories with the release version as outlined in the [documentation](gh_release/README.md)
1. Merge the release code into the master branch from [master update strategy](strategies/master-updates.md)
1. Change the branching rules to lock the branch for any further changes until next planned release.
1. Release check shall be performed as per [Release checks](docs/release-check.md).

# MOSIP Post Release Process
1. Execute the [Post-Release Preparation](https://github.com/mosip/release-script/actions/workflows/post-release-changes.yml) workflow to replace the "RELEASE_URL" with "OSSRH_SNAPSHOT_URL" to the release branch.
1. while running manual workflow, it will ask for the following inputs as below:
    * Repo URL ( EX. mosip/< repo name > ): Name of the owner of the repository and repository name.
    * Repo Branch: It should be the release-branch.
    * base branch for PR: It should be the release-branch.
    * Next click on `run workflow`.
1. Ensure to update the Helm `Chart.yaml` and `install.sh` files to reflect the release version with the `-develop` suffix ( Ex. 1.3.0-develop ).
1. Review and merge the pull request created by release bot from `releas-branch` to the respective release repository.

# MOSIP Developer-Preview-Release Process
* Please refer to the [Documentation](docs/developer-preview-release.md) for the Developer Preview-Release Process.
### NOTE:
1. Avoid publishing `artifacts` from Nexus staging repositories for developer-preview-release.
1. Avoid merging release code into the `master branch` developer-preview-release.

# GitHub manual workflow to images transfer
* Please refer to Image transfer from [here](vidivi/README.md)

# Tagging of Repos Workflow
* Please refer to the Tagging of Repos link to [here](gh_release/README.md)
* 
# MOSIP Release Preparation

## Overview
Use this guide to release specific MOSIP version.

## Pre-requisites
* All the pre-requisites are mentioned in [pre-requisites guide](docs/pre-requisites.md).
* Make sure proper branching rules are followed. For more details see [MOSIP repo Branching Rules](https://github.com/mosip/release-script/blob/release-1.2.0.1/release/docs/branching-rule.md).
## MOSIP Release Process
01. Create `release-branch` from the release-candidate branch and name it as below:
    ```
    release-<release-version>
    eg: release-1.3.x
    ```
02. The `pom.xml` files should be updated with the release version of SNAPSHOT in the release branch ( Ex. release-1.3.x ).
    * If not, please coordinate with the developer to ensure it is updated.
03. Ensure that the `db_upgrade` and `db_rollback` scripts are updated with the latest release version.
    * If not, please coordinate with the developer to ensure it is updated.
04. Execute the ```Release/Pre-release Preparation``` by running the [Action](https://github.com/mosip/release-script/actions/workflows/release-changes.yml).
    * Below inputs for `Release/Pre-release Preparation`
      * Repo URL ( e.g., mosip/< repo name > )
      * Repo Branch  ( e.g., release-1.3.x )
      * tag to update ( update release version Ex. 1.3.0 )
      * tag to be replaced ( replace SNAPSHOT version Ex. 1.3.0-SNAPSHOT )
      * base branch for PR ( e.g., release-1.3.x )
      * Next click on ```run workflow```
05. Review and merge the pull request created by release bot from releas-branch to the respective release repository. While reviewing the Pull Request keep note of the below points:
    * Ensure that the latest POM version updates are reflected across all POM files.
    * Ensure that there are no SNAPSHOT versions in the Pull Request or the respective release branch.
    * It should remove the `-DskipTests` references from all the triggers so that tests are not skipped while building and release and analysis.
    * If PR contains changes in Dockerfile for changing `libs-snapshot-local` reference to `libs-release-local`.
        * If this instance is found in the Dockerfile, update the same to `artifactory-ref-impl` repo owner so that it can be handled in the artifactory docker image as well
06. Ensure that the Helm `Chart.yaml` is updated with the release version, and modify `install.sh` accordingly. Additionally, update `values.yaml` with the latest released Docker image version.
07. After all changes are merged into the release branch, wait for the GitHub Actions workflow to complete, which includes the following builds:
    * Maven Build
    * Docker Build
    * Publish to Nexus
    * Sonar Analysis
    * Helm Chart Publish
08. Log in to [Nexus](https://oss.sonatype.org/#welcome) to release the artifacts to Maven Central.
    * Ensure that all artifacts are in a closed state in the Nexus staging repository
    * Ensure that all artifact versions match the release version.
    * Click on `Release` Staging Repositories to release the artifacts to Maven Central.
09. Verify that the released artifacts are present on [Maven central](https://repo1.maven.org/maven2/io/mosip/)
10. Tag the respective release repositories with the release version as outlined in the [documentation](https://github.com/mosip/release-script/blob/release-1.2.0.1/release/gh_release/README.md)
11. Perform the image transfer from `mosipdev` to `mosipid` using the release version from [here](https://github.com/mosip/release-script/blob/release-1.2.0.1/release/vidivi/README.md)
    * Ensure that the Docker tag is updated correctly with the release version.
12. Create a `DSD/MOSIP` ticket for image signing by the Security team.
13. Merge the release code into the master branch.

## MOSIP Post Release Process
01. Execute the [Post-Release Preparation](https://github.com/mosip/release-script/actions/workflows/post-release-changes.yml) workflow to replace the "RELEASE_URL" with "OSSRH_SNAPSHOT_URL" to the release branch.
02. while running manual workflow it will ask for workflow inputs as below
    * Repo URL ( EX. mosip/< repo name > ): Name of the owner of the repository and repository name.
    * Repo Branch: It should be release-branch.
    * base branch for PR: It should be release-branch.
    * Next click on `run workflow`.
03. Ensure to update the Helm `Chart.yaml` and `install.sh` files to reflect the release version with the `-develop` suffix ( Ex. 1.3.0-develop ).
04. Review and merge the pull request created by release bot from releas-branch to the respective release repository.

## MOSIP Developer-Pre-Release Process
* Please refer to the [Documentation](https://github.com/mosip/release-script/blob/release-1.2.0.1/release/docs/developer-pre-release.md) for the Developer Pre-Release Process.

## GitHub manual workflow to transfer images
Steps to run transfer images from one docker hub account to another.
* Update the docker images list in the [images.txt](https://github.com/mosip/release-script/blob/release-1.2.0.1/release/vidivi/images.txt) file.
* Execute the `Manual workflow to transfer image` GitHub Action from **release-script** repopository.
* while running manual workflow it will ask for workflow inputs as below .
  * branch: select specific branch
  * provide docker hub username: username of the destination dockerhub account
  * provide docker hub token: password/token of the destination dockerhub account.
  * provide docker hub destination org: destination dockerhub organisation.
  * Next click on `run workflow`.
* Cross verify in hub.docker Image are transferred or not.

# Tagging of Repos Workflow

## Purpose

This workflow automates the process of creating GitHub releases by applying tags to your repositories through the GitHub API. It allows for the generation of both regular releases and pre-releases.It takes inputs dynamically from a CSV file.
The workflow can be triggered based on your specific release criteria.

## Inputs

The workflow accepts the following inputs:
- `CSV_FILE` (required:false, string, default: ./release/gh_release/repos.csv): This input specifies the path to the CSV file. The content of the CSV file should adhere to the format: `REPO, TAG, ONLY_TAG, BRANCH, LATEST, BODY, PRE_RELEASE, DRAFT, MESSAGE`.
    - `REPO` : The name of the repository without the .git extension. The name is not case sensitive.
    - `TAG` : The tag that you want to create and publish.
    - `ONLY_TAG` : Set to true if you want to create only a tag without a full release.
    - `BRANCH` : The name of the branch from which the release will be created.
    - `LATEST` : Set to false to prevent marking the release as the latest.
    - `BODY` : A custom message for the release body, describing the changes in this release.
    - `PRE_RELEASE` : A boolean (True/False) indicating whether the release is a pre-release or not.
    - `DRAFT` : A boolean (True/False) indicating whether the release should be a draft.
    - `MESSAGE` : The tag message.
  
## Secrets

This workflow requires the following secrets to be set in your GitHub repository:
- `SLACK_WEBHOOK_URL` (required): The Slack webhook URL for sending notifications about the workflow's progress and outcome.
- `TOKEN` (required): The token required for authenticating and authorizing the release operation.

## Example Usage

Here's an example of how you can use this workflow to create a release:
```yaml
name:  workflow for mosip github releases

on:
  workflow_dispatch:
    inputs:
      CSV_FILE:
        description: path of csv file
        required: false
        type: string
        default: ./release/gh_release/repos.csv
jobs:
  workflow-tag:
    needs: chk_token
    uses: mosip/kattu/.github/workflows/tag.yaml@master
    with:
      CSV_FILE: ${{ inputs.CSV_FILE }}
    secrets:
      TOKEN: "${{ secrets.TOKEN }}"
      SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```
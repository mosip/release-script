# MOSIP Modules Release Process
* The ```pom.xml``` files should be updated with the release version of SNAPSHOT in the release branch ( Ex. release-1.3.x ).
    * If not, please coordinate with the developer to ensure it is updated.
* Ensure that the ```db_upgrade``` and ```db_rollback``` scripts are updated with the latest release version.
    * If not, please coordinate with the developer to ensure it is updated.
* Execute the ```Release/Pre-release Preparation``` by running the [Action](https://github.com/mosip/release-script/actions/workflows/release-changes.yml).
* Input for Release/Pre-release Preparation
    * Repo URL ( Ex. mosip/< repo name > )
    * Repo Branch  ( Ex. release-1.3.x )
    * tag to update ( update release version Ex. 1.3.0 )
    * tag to be replaced ( replace SNAPSHOT version Ex. 1.3.0-SNAPSHOT )
    * base branch for PR ( Ex. release-1.3.x )
    * Next click on ```run workflow```
* Upon execution of the Release/Pre-release Preparation workflow, an automatically generated pull request will be created in the respective release repository.
    * Ensure that the release version is correctly updated in the Pull Request.
    * Ensure that there are no SNAPSHOT versions in the Pull Request or the respective release branch.
    * Obtain approval for the Pull Request and have it merged by the DevOps lead.
* Ensure that the Helm ```Chart.yaml``` is updated with the release version, and modify ```install.sh``` accordingly. Additionally, update ```values.yaml``` with the latest released Docker image version.
* After all changes are merged into the release branch, wait for the GitHub Actions workflow to complete, which includes the following builds:
    * Maven Build
    * Docker Build
    * Publish to Nexus
    * Sonar Analysis
    * Helm Chart Publish
* Log in to [Nexus](https://oss.sonatype.org/#welcome) to release the artifacts to Maven Central.
    * Ensure that all artifacts are in a closed state in the Nexus staging repository
    * Ensure that all artifact versions match the release version.
    * Click on ```Release``` Staging Repositories to release the artifacts to Maven Central.
* Verify that the released artifacts are present on [Maven central](https://repo1.maven.org/maven2/io/mosip/)
* Tag the respective release repositories with the release version as outlined in the [documentation](https://github.com/mosip/release-script/blob/release-1.2.0.1/release/gh_release/README.md)
* Perform the image transfer from ```mosipdev``` to ```mosipid``` using the release version from [here](https://github.com/mosip/release-script/blob/release-1.2.0.1/release/vidivi/README.md)
    * Ensure that the Docker tag is updated correctly with the release version.
* Create a `DSD/MOSIP` ticket for image signing by the Security team.
* Merge the release code into the master branch.

# MOSIP Modules Developer-Pre-Release Process
* The ```pom.xml``` files should be updated with the release version of SNAPSHOT in the release branch ( Ex. release-1.3.x ).
    * If not, please coordinate with the developer to ensure it is updated.
* Ensure that the ```db_upgrade``` and ```db_rollback``` scripts are updated with the latest release version.
    * If not, please coordinate with the developer to ensure it is updated.
* Execute the ```Release/Pre-release Preparation``` by running the [Action](https://github.com/mosip/release-script/actions/workflows/release-changes.yml).
* Input for Release/Pre-release Preparation
    * Repo URL ( Ex. mosip/< repo name > )
    * Repo Branch  ( Ex. release-1.3.x )
    * tag to update ( update release version Ex. 1.3.0 )
    * tag to be replaced ( replace SNAPSHOT version Ex. 1.3.0-SNAPSHOT )
    * base branch for PR ( Ex. release-1.3.x )
    * Next click on ```run workflow```
* Upon execution of the Release/Pre-release Preparation workflow, an automatically generated pull request will be created in the respective release repository.
    * Ensure that the release version is correctly updated in the Pull Request.
    * Ensure that there are no SNAPSHOT versions in the Pull Request or the respective release branch.
    * Obtain approval for the Pull Request and have it merged by the DevOps lead.
* Ensure that the Helm ```Chart.yaml``` is updated with the release version, and modify ```install.sh``` accordingly. Additionally, update ```values.yaml``` with the latest released Docker image version.
* After all changes are merged into the release branch, wait for the GitHub Actions workflow to complete, which includes the following builds:
    * Maven Build
    * Docker Build
    * Publish to Nexus
    * Sonar Analysis
    * Helm Chart Publish
* Tag the respective release repositories with the release version as outlined in the [documentation](https://github.com/mosip/release-script/blob/release-1.2.0.1/release/gh_release/README.md)
* Perform the image transfer from ```mosipdev``` to ```mosipid``` using the release version from [here](https://github.com/mosip/release-script/blob/release-1.2.0.1/release/vidivi/README.md)
    * Ensure that the Docker tag is updated correctly with the release version.
* Create a `DSD/MOSIP` ticket for image signing by the Security team.

#### NOTE: 
1. Avoid publishing artifacts from Nexus staging repositories.
2. Avoid merging release code into the master branch.

# MOSIP Post Release Process
* Execute the [Post-Release Preparation](https://github.com/mosip/release-script/actions/workflows/post-release-changes.yml) workflow to replace the "RELEASE_URL" with "OSSRH_SNAPSHOT_URL" to the release branch.
* while running manual workflow it will ask for workflow inputs as below
    * Repo URL ( EX. mosip/< repo name > ): Name of the owner of the repository and repository name.
    * Repo Branch: It should be release-branch.
    * base branch for PR: It should be release-branch.
    * Next click on `run workflow`.
* Ensure to update the Helm `Chart.yaml` and `install.sh` files to reflect the release version with the `-develop` suffix ( Ex. 1.3.0-develop ).

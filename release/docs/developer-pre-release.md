# MOSIP Developer-Pre-Release Process
01. The ```pom.xml``` files should be updated with the release version of SNAPSHOT in the release branch ( Ex. release-1.3.x ).
    * If not, please coordinate with the developer to ensure it is updated.
02. Ensure that the ```db_upgrade``` and ```db_rollback``` scripts are updated with the latest release version.
    * If not, please coordinate with the developer to ensure it is updated.
03. Execute the ```Release/Pre-release Preparation``` by running the [Action](https://github.com/mosip/release-script/actions/workflows/release-changes.yml).
04. Input for Release/Pre-release Preparation
    * Repo URL ( Ex. mosip/< repo name > )
    * Repo Branch  ( Ex. release-1.3.x )
    * tag to update ( update release version Ex. 1.3.0 )
    * tag to be replaced ( replace SNAPSHOT version Ex. 1.3.0-SNAPSHOT )
    * base branch for PR ( Ex. release-1.3.x )
    * Next click on ```run workflow```
05. Upon execution of the Release/Pre-release Preparation workflow, an automatically generated pull request will be created in the respective release repository.
    * Ensure that the release version is correctly updated in the Pull Request.
    * Ensure that there are no SNAPSHOT versions in the Pull Request or the respective release branch.
    * Obtain approval for the Pull Request and have it merged by the DevOps lead.
06. Ensure that the Helm ```Chart.yaml``` is updated with the release version, and modify ```install.sh``` accordingly. Additionally, update ```values.yaml``` with the latest released Docker image version.
07. After all changes are merged into the release branch, wait for the GitHub Actions workflow to complete, which includes the following builds:
    * Maven Build
    * Docker Build
    * Publish to Nexus
    * Sonar Analysis
    * Helm Chart Publish
08. Tag the respective release repositories with the release version as outlined in the [documentation](https://github.com/mosip/release-script/blob/release-1.2.0.1/release/gh_release/README.md)
09. Perform the image transfer from ```mosipdev``` to ```mosipid``` using the release version from [here](https://github.com/mosip/release-script/blob/release-1.2.0.1/release/vidivi/README.md)
    * Ensure that the Docker tag is updated correctly with the release version.
10. Create a `DSD/MOSIP` ticket for image signing by the Security team.

#### NOTE:
01. Avoid publishing artifacts from Nexus staging repositories.
02. Avoid merging release code into the master branch.


# MOSIP Developer-Pre-Release Process
1. The `pom.xml` files should be updated with the release version of SNAPSHOT in the release branch ( Ex. release-1.3.x ).
    * If not, please coordinate with the developer to ensure it is updated.
1. Ensure that the `db_upgrade` and `db_rollback` scripts are updated with the latest release version.
    * If not, please coordinate with the developer to ensure it is updated.
1. Perform the image transfer from `mosipdev` to `mosipid` using the release version from [here](../vidivi/README.md)
    * Ensure that the Docker tag is updated correctly with the release version.
1. Create a `DSD/MOSIP` ticket for image signing by the Security team.
1. Tag the respective release repositories with the release version as outlined in the [documentation](../gh_release/README.md)


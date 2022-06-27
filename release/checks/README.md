# Release check
* This guide contains checks to be performed once Release process ends.
* Release checks should must not be performed by the Release team.
* Release check contains:
    * checking if artifacts are release.
    * checking if docker images are published.
    * checking if proper tagging is done for all the listed repositories.

## Checks
* All the artifacts for release verson of different MOSIP modules are released and published to Maven Central Repository.
    * All the artifacts released as part of MOSIP are present on Maven Central in `io/mosip` group id.
    * URL: https://repo1.maven.org/maven2/io/mosip/ .
    * Crosscheck if the artifacts are present for specific release version.
    ```
    https://repo1.maven.org/maven2/<group-id>/<release-version>/
    eg.
    https://repo1.maven.org/maven2/io/mosip/commons/1.2.0/
    ```
* All the docker images are pushed to `mosipid` dockerhub organisation.
    * Tag to be checked will be <release_version>
    * Use [vidivi script](../vidivi/README.md) in the check mode to check the existence.
    * Docker images to be checked are [listed](./images.txt). Please crosscheck once.

* All the repositories are tagged or not.
    * List all the repositories to be released in the [repos.txt](./repos.txt).
    * Execute the `check_tag.sh` to check if the inputed tag is present in all the repositories as listed in [repos.txt](./repos.txt).
    * Result of the check operation is stored in [result.txt](./result.txt)

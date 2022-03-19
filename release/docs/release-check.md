# Release check
* This guide contains checks to be performed once Release process ends.
* Release checks should must not be performed by the Release team.

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
    * 

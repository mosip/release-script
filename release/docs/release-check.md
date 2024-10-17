# Release check
1. Verify that the released artifacts are present on [Maven central](https://repo1.maven.org/maven2/io/mosip/)
1. Confirm that the specified release version `Tag` is present on the release repository which includes release version.
1. Verify the version of the Helm chart in the `mosip-helm` repository, you can add the repository using the following command:
```
 helm repo add mosip https://mosip.github.io/mosip-helm
```
1. This command allows you to view the available charts and their versions, which are published on the [gh-pages branch](https://github.com/mosip/mosip-helm/tree/gh-pages). The charts are packaged in `.tgz` format and manually pushed to the `gh-pages branch`. You can cross-check the versions by examining the repository's `index.yaml` file located in that branch.
1. verify that a Docker image has been updated with a [release tag](https://hub.docker.com/) ( e.g., mosipid/< image name >:< release version > )

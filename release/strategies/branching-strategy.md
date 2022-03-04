# MOSIP Branching Strategies

## Branch categories
* Default branch in all the MOSIP repos are master branch.
* `master` branch contains latest released code there for MOSIP.
* Default branch for release will be named as `release-<version>`.
* Development activities continues on `develop` branch.
* Release testing occurs on the code from `<version>-rc<release-candidate-version>`. for eg. 1.2.0-rc1, 1.1.5-rc1
* Branch used by automated bot's for making release changes is `release-branch`
* Branch named after MOSIP jira id's are the branches working on specific major change as described in defined Jira ticket.

## Branching rules
* `develop` branch always contains the latest code in development mode.
* `rc` branch consists of the latest release candidate code for each repos with release candidate no.
* `release` branch contains released code for specific versions.
* branches with specific MOSIP version prior to 1.2.0 contains the codebase for the same version. Do use the tested and released code by checking the release versions.
* after after every release `master` get updated with the latest codebase there from release branch.

## Locking branches
* Changes on `develop` branches can be approved and merged by the repo admins there.
* Changes to `rc` and `release` branch can only be merged by build & release team member after approval from Dev lead there.
* After release the branches are locked so that no more changes can be merged on the same.


## Taging branches.
* In MOSIP we tag the branches normally for pre-release or complete release or release with specific required funtionality.
* Release branches are tagged only after all the artifacts are released to Maven Central and images are pushed to the `mosipdev` dockerhub organisaton.
* Also the branches needed to be locked after release and before release so that no unnecesary commit can be merged to the same.

## Overall Branching strategy
* Branching strategy at MOSIP can be explained by this [pic](../docs/branching.png)

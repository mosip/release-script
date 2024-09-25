# Branching rules Setup for release-branch
* Navigate to the `Settings` of the release repository.
* Select `Add rule` 
* Include the release branch name (e.g., release-1.3.x).
* Select the following checks:
    * Require a pull request before merging
      * Require approvals
    * Require status checks to pass before merging
      * Add Status check (e.g., build-commons / maven-build, kernel-config-server / build-dockers...)
    * Require conversation resolution before merging
    * Do not allow bypassing the above settings
    * Restrict who can push to matching branches
      * Restrict pushes that create matching branches
      * Provide following usernames
      * gsasikumar
      * ckm007
      * vishwa-vyom
    * Select Create.
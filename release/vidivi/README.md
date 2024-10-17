# Vidivi
* `Vidiv.py` script here is used to transfer docker images as part of release process between different MOSIP organisations in dockerhub.

## Overview
* In MOSIP we have specifically below mentioned dockerhub organisations. Below are the details:
    * `mosipid ` :- This dockerhub organisation contains docker images which are officially released for Open Source Community.
    * `mosipint` :-
        * This dockerhub organisation contains docker images which are not officially released for Open Source Community but is eligile to be used for some specific implementation. 
        * Moving ahead the images from this dockerhub organisation will be moved to `mosipid`. 
        * Mostly it contains patches to be provided for services untill the same patch is fully released.
        * It also contains the backup of the qa tested images in the previous passed internal sprint by QA team.
    * `mosipdev` :- This dockerhub organisation contains docker images which are in development phase.
    * `mosipqa` :- This dockerhub organisation is used to hold all the docker images being provided to QA team for testing.
* As part of github action docker images from all the modular github repositories are created and published to mosipdev.
* After completion of all QA testing cycles, docker images are released from `mosipdev` to `mosipid` or `mosipint` dockerhub organisation as per requirement.

## Docker image lifecycle:

* `mosipdev` --> `mosipqa` --> `mosipint` --> `mosipid`
* mosipdev: newly created images undergoing dev testing.
* mosipqa: images which passed dev cycle and is passed to QA team for qa testing.
* mosipint: images which are verified by QA team. These mainly are the stable performing docker images from the previous sprint.
* mosipid: images released after qa testing.

## GitHub manual workflow to transfer images
Steps to transfer Docker images from one Docker Hub account to another.
* Update the list of Docker images in the [images.txt](vidivi/images.txt) file.
* Execute the [Manual workflow to transfer image](https://github.com/mosip/release-script/actions/workflows/image-transfer.yml) GitHub Action from **release-script** repo.
* While running the manual workflow, provide the following inputs:
  * `branch`: select the specific branch
  * `provide docker hub username`: username of the destination dockerhub account
  * `provide docker hub token`: password/token of the destination dockerhub account.
  * `provide docker hub destination org`: destination dockerhub organisation.
  * Next click on `run workflow`.

**Note**: `source tag` and `destination tag` should be **spaces** separated.
* verify that a Docker image has been updated with a [tag](https://hub.docker.com/) ( e.g., mosipid/< image name >:< version > )

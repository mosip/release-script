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

## Pre-requisites
* Install `Python3`. Refer [Python3 Installation guide](https://realpython.com/installing-python/) for OS specific steps.
* Install `docker` using `pip3`
```
sudo pip3 install docker
sudo pip3 install pyYaml
sudo pip3 install requests
sudo pip3 install logging
sudo pip3 install datetime
```

## Use
* Set the below mentioned parameters in [config](config.yml).
    * `username` : username of the destination dockerhub account.
    * `token` : password/token of the destination dockerhub account.
    * `destination_organisation` : destination dockerhub organisation.
    * `registry_url` : destination docker registry URL. By default set to the dockerhub Url.
    * `filename` : filename for the list of docker images to be moved. 
* Update the docker images list in the [images.txt](images.txt) file. Below are the guidelines for the same:
   * the image name and image tag will be `spaces` separated or colon `:`. eg.
   ```
   <source-organisation>/<docker-image-name>:<source tag>
   mosipdev/kernel-auth-service:1.2.0
   ```
   ```
   <source-organisation>/<docker-image-name>               <source tag>
   mosipdev/kernel-auth-service                            1.2.0
   ```
   * If source and destination tag are different set image list as:
   ```
   <source-organisation>/<docker-image-name>:<source tag>    <destination-tag>
   mosipdev/kernel-auth-service:release-1.2.0                1.2.0
   ```
   Note: `source tag` and `destination tag` should be spaces separated.

* The script will also create a log file with format `vidiv-datetime.log` in current directory.
* Run `vidivi.py` to check the existence of docker images from the source organization.
  ```
  sudo python3 vidivi.py check
  ```
* Run `vidivi.py` to check the existence of docker images from the source and destination organization. 
  Also, will compare the docker image HASH ID between source and destination organization if destination organization exists.
  ```
  sudo python3 vidivi.py hash
  ```
* Run `vidivi.py` to move the docker images.
  ```
  sudo python3 vidivi.py push
  ```

# Update master

* After release the release `master` branch needed to be updated with the latest code over there from the `release` branch.
* Basically we don't specifically merge to master instead we overide the `master` branch with latest code from `release` branch.
* Commands used for the same:
```
git fetch --all
git checkout <branch to release>
git pull origin
git checkout master
git pull master
git reset --hard origin/<branch to release>
git push -f origin master
```
* Once the latest code is merged back to the `master` do update the badges to point to the master branch.

NOTE: 
Change the branching rules for `master` to all forced pushes before performing the force push to the repo.


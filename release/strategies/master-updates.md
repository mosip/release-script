# Update master

* After release master branch needed to be updated with the latest code from release branch.
* We don't merge to master instead we overide the `master` branch with latest code from `release` branch.
* Below are the commmands to updates master branch with latest code from release branch:
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
Change the branching rules for `master` to allow forced pushes before performing the force push and then also revert back the same once pushed.

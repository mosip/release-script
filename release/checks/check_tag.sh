#!/bin/bash
# Script is used to check if tag exists for all the repo names mentioned in the repos.txt file.
# The script needs the tag to be checked after release in all the repos.

echo Please mention the tag to be searched in all the repos.
read search
echo Removing previously existing resutlts.txt file if any.
rm -f result.txt

URL1='git ls-remote --sort='version:refname' --tags https://github.com/mosip/'

URL2='.git | cut --delimiter='/' --fields=3 | '

URL3='grep '$search$

#while true; do for X in '-' '/' '|' '\'; do echo -en "\b$X"; sleep 0.1; done; done 

echo Checking presence of $search in all the repositories.

#for repo in $(cat repos.txt);do
while read repo ; do


for X in '-' '/' '|' '\'; do echo -en "\b$X"; sleep 0.1; done;

URL="$URL1$repo$URL2$URL3"
tag=`eval "$URL"`
if ! [[ $tag ]];then
echo Tag is not Present for $repo >> result.txt
fi
unset tag
done < repos.txt

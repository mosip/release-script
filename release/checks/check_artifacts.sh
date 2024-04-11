#!/bin/bash
# Script is used to check if artifacts are released to maven central as per the artifacts group and name given in artifacts.txt.
# Script needs artifact.txt to be present with  details of group and artifacts name.

echo Please mention the version of artifact to be searched for all the modules.
read search
echo Removing previously existing resutlts.txt file if any.
rm -f result.txt

URL1='curl -v https://repo1.maven.org/maven2/io/mosip/'

URL2='maven-metadata.xml 2>&1 | grep ">'$search'<" '

echo Checking presence of artifact with version $search for all the modules.

#for repo in $(cat artifacts.txt);do
while read artifact ; do


for X in '-' '/' '|' '\'; do echo -en "\b$X"; sleep 0.1; done;

URL="$URL1$artifact$URL2"
version=`eval "$URL"`
if ! [[ $version ]];then
echo artifact is not Present for $search for $artifact >> result.txt
fi
unset version
done < artifact.txt

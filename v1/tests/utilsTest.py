import unittest

from paths import logPath
from utils import Command, init_logger, myprint, match
import config as conf
init_logger(logPath)


class MyTestCase(unittest.TestCase):

    def testCommand(self):
        Command(['java', '-version'])

    def testCommandWrong(self):
        Command(['java', '--verion'])

    def testMatch(self):
        data = '</properties> </profile> <profile> <id>allow-snapshots</id>      \n ' \
               '<activation><activeByDefault>true</activeByDefault></activation> <repositories> <repository>        ' \
               '<id>snapshots-repo</id> <url>https://oss.sonatype.org/content/repositories/snapshots</url> ' \
               '<releases><enabled>false</enabled></releases> <snapshots><enabled>true</enabled></snapshots> ' \
               '</repository>  <repository>         <id>releases-repo</id>  ' \
               '<url>https://oss.sonatype.org/service/local/staging/deploy/maven2</url>         ' \
               '<releases><enabled>true</enabled></releases>         <snapshots><enabled>false</enabled></snapshots> ' \
               '</repository> </repositories>  </profile> <profile> <id>sonar</id> <properties>  ' \
               '<sonar.sources>.</sonar.sources> <sonar.host.url>https://sonarcloud.io</sonar.host.url>  ' \
               '</properties> <activation> <activeByDefault>false</activeByDefault> </activation> </profile> ' \
               '</profiles> </settings>" > $GITHUB_WORKSPACE/settings.xml '
        myprint(match(conf.release_repo_identifier, data))
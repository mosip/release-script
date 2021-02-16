import unittest

from actions.common import isMosipDep, checkIfParentPom, \
    getVersionsFromPom, updateVersions
from actions.dependency import Dependency
from paths import testPomPath, logPath, testNewPomPath, testParentPomPath
from utils import init_logger, myprint
init_logger(logPath)


class MyTestCase(unittest.TestCase):

    def testIsMosipDep(self):
        myprint(isMosipDep("kernel.core.version"))

    def testcheckIfParentPom(self):
        myprint('is parent pom')
        myprint(checkIfParentPom(testParentPomPath))

    def testGetVersionsFromPom(self):
        myprint(getVersionsFromPom(testPomPath))

    def testUpdateVersionsInPom(self):
        myprint(updateVersions(testParentPomPath, '1.1.5', testNewPomPath))

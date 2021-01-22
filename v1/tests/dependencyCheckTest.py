import unittest

from actions.common import getPropertiesFromPom, isMosipDep, updatePropertiesInPom, checkIfParentPom, \
    getVersionsFromPom, updateVersionsInPom
from actions.dependency import Dependency
from paths import testPomPath, logPath, testNewPomPath, testParentPomPath
from utils import init_logger, myprint
init_logger(logPath)


class MyTestCase(unittest.TestCase):

    def testLoadPom(self):
        getPropertiesFromPom(testPomPath)

    def testIsMosipDep(self):
        myprint(isMosipDep("kernel.core.version"))

    def testUpdatePropertiesInPom(self):
        updatePropertiesInPom(testPomPath, '1.1.4', testNewPomPath)

    def testcheckIfParentPom(self):
        myprint('is parent pom')
        myprint(checkIfParentPom(testParentPomPath))

    def testGetVersionsFromPom(self):
        myprint(getVersionsFromPom(testPomPath))

    def testUpdateVersionsInPom(self):
        myprint(updateVersionsInPom(testParentPomPath, '1.1.5', testNewPomPath))

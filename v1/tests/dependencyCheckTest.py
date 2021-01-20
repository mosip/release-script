import unittest

from actions.dependency import Dependency
from paths import testPomPath, logPath, testNewPomPath
from utils import init_logger, myprint

init_logger(logPath)


class MyTestCase(unittest.TestCase):

    def testLoadPom(self):
        Dependency().getPropertiesFromPom(testPomPath)

    def testIsMosipDep(self):
        myprint(Dependency().isMosipDep("kernel.core.version"))

    def testUpdatePropertiesInPom(self):
        Dependency().updatePropertiesInPom(testPomPath, '1.1.4', testNewPomPath)

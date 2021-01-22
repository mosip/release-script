import unittest

from paths import logPath
from utils import Command, init_logger, myprint
init_logger(logPath)


class MyTestCase(unittest.TestCase):

    def testCommand(self):
        Command(['java', '-version'])

    def testCommandWrong(self):
        Command(['java', '--verion'])
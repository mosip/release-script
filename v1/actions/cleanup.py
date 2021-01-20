import os
import shutil

from paths import reposFolder
from utils import myprint


def Cleanup():
    cleanReposFolder()


def cleanReposFolder():
    if os.path.exists(reposFolder):
        myprint("Removing directory: "+reposFolder)
        shutil.rmtree(reposFolder)

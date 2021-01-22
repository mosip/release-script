import os
import re
import shutil

from paths import reposFolder, generatedDataFolderPath
from utils import myprint


def Cleanup():
    cleanReposFolder()
    cleanGeneratedData()


def cleanReposFolder():
    if os.path.exists(reposFolder):
        myprint("Removing directory: "+reposFolder)
        shutil.rmtree(reposFolder)


def cleanGeneratedData():
    for f in os.listdir(generatedDataFolderPath):
        if re.search(r'.*\.json', f):
            file_path = os.path.join(generatedDataFolderPath, f)
            myprint("Removing "+file_path)
            os.remove(file_path)

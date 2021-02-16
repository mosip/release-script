import os
import re
import shutil

from paths import reposFolder, generatedDataFolderPath, mavenRepoPath
from utils import myprint


def Clean():
    myprint("Removing repo folders: ", 2)
    cleanReposFolder()

    myprint("Removing generated data files: ", 2)
    cleanGeneratedData()

    myprint("Removing maven local repo: ", 2)
    cleanMavenData()


def cleanReposFolder():
    if os.path.exists(reposFolder):
        myprint("Removing directory: " + reposFolder)
        shutil.rmtree(reposFolder)


def cleanGeneratedData():
    for f in os.listdir(generatedDataFolderPath):
        if re.search(r'.*\.json', f):
            file_path = os.path.join(generatedDataFolderPath, f)
            myprint("Removing " + file_path)
            os.remove(file_path)


def cleanMavenData():
    if os.path.exists(mavenRepoPath):
        myprint("Removing directory: " + mavenRepoPath)
        shutil.rmtree(mavenRepoPath)

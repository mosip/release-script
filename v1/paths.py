import os

# Maven local repo
from pathlib import Path

home = str(Path.home())

mavenRepoPath = os.path.abspath(
    os.path.join(home, '.m2', 'repository', 'io', 'mosip')
)

# Env file path
envPath = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), './', '.env')
)

rootPath = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), './')
)

logPath = os.path.abspath(
    os.path.join(rootPath, 'out.log')
)

generatedDataFolderPath = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), './', 'generatedData')
)

reposFolder = os.path.join(generatedDataFolderPath, '..', '..', '..', 'repos')

repoListDataPath = os.path.join(rootPath, 'inputData', 'repoList.json')

# Resources
resourcesPath = os.path.abspath(
    os.path.join(rootPath, 'resources')
)
testPomPath = os.path.abspath(
    os.path.join(resourcesPath, 'testPom.xml')
)
testNewPomPath = os.path.abspath(
    os.path.join(resourcesPath, 'newTestPom.xml')
)
testParentPomPath = os.path.abspath(
    os.path.join(resourcesPath, 'testParentPom.xml')
)
testDiffParentPomPath = os.path.abspath(
    os.path.join(resourcesPath, 'testDiffParentPom.xml')
)
# Action's result path
verifyBranchResult = os.path.join(generatedDataFolderPath, 'branchVerification.json')
checkoutResult = os.path.join(generatedDataFolderPath, 'checkout.json')
depCheckResult = os.path.join(generatedDataFolderPath, 'dependencyCheck.json')
depCheckDetailedResult = os.path.join(generatedDataFolderPath, 'dependencyCheckDetailed.json')
depUpdateResult = os.path.join(generatedDataFolderPath, 'dependencyUpdate.json')
releaseUrlUpdateResult = os.path.join(generatedDataFolderPath, 'releaseUrlUpdate.json')
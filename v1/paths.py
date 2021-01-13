import os

envPath = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), './', '.env')
)

generatedDataFolderPath = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), './', 'generatedData')
)

reposFolder = os.path.join(generatedDataFolderPath, '..', '..', '..', 'repos')

repoListDataPath = os.path.join(generatedDataFolderPath, 'repoList.json')

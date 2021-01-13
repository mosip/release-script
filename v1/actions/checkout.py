import os

from paths import repoListDataPath, reposFolder
from utils import get_json_file, myprint, Command, getRepoNameFromUrl
import config as conf


class Checkout:

    def __init__(self):
        self.repos = self.fetchRepoList()
        self.checkoutRepos()

    def fetchRepoList(self):
        repos = get_json_file(repoListDataPath)
        myprint("List of repos")
        myprint(repos)
        return repos

    # git clone <url> --branch <branch> --single-branch [<folder>]
    def checkoutRepos(self):
        for repo in self.repos:
            repo_name = getRepoNameFromUrl(repo)
            repo_path = os.path.join(reposFolder, repo_name)
            myprint("Checking out repo "+repo_name+" at "+repo_path, 2)
            Command(['git', 'clone', repo, '--branch', conf.branch_name, '--single-branch', repo_path])

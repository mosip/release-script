import os
from typing import List

from classes.repoInfo import RepoInfo
from paths import reposFolder, checkoutResult, verifyBranchResult
from utils import get_json_file, myprint, Command, getRepoNameFromUrl, write_json_file, get_json_file_cls


class Checkout:

    def __init__(self):
        self.repos: List[RepoInfo] = get_json_file_cls(verifyBranchResult, RepoInfo)

    # git clone <repo url> --branch <branch> --single-branch [<folder>]
    def checkoutRepos(self):
        output = []
        for repo in self.repos:
            repo_path = os.path.abspath(os.path.join(reposFolder, repo.repo_short))
            myprint("Checking out repo " + repo.repo_short + " at " + repo_path, 2)
            Command(['git', 'clone', repo.repo, '--branch', repo.branch, '--single-branch', repo_path])
            output.append(repo.set_repo_path(repo_path).__dict__)
        write_json_file(checkoutResult, output)

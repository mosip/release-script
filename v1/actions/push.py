from typing import List

from classes.repoInfo import RepoInfo
from paths import checkoutResult, reposFolder
from utils import get_json_file_cls, myprint, Command, getGitDirAndWorkTree


class Push:

    def __init__(self):
        self.repos: List[RepoInfo] = get_json_file_cls(checkoutResult, RepoInfo)

    # git commit -am "<commit message>"
    def pushRepos(self):
        for repo in self.repos:
            git_dir, work_tree = getGitDirAndWorkTree(repo.repo_path)
            myprint("Pushing changes to repo " + repo.repo_short + " for " + repo.branch + " branch ", 2)
            Command(['git', git_dir, work_tree, 'push'], True)

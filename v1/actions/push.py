import os
from typing import List

from classes.repoInfo import RepoInfo
from paths import checkoutResult, reposFolder
from utils import get_json_file_cls, myprint, Command


class Push:

    def __init__(self):
        self.repos: List[RepoInfo] = get_json_file_cls(checkoutResult, RepoInfo)

    # git commit -am "<commit message>"
    def pushRepos(self):
        for repo in self.repos:
            repo_path = os.path.abspath(os.path.join(reposFolder, repo.repo_short))
            myprint("Push changes for repo " + repo.repo_short + " [" + repo_path + "]", 2)
            Command(['git', 'push', repo_path])

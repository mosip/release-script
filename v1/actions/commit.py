import os
from typing import List

from classes.repoInfo import RepoInfo
from paths import checkoutResult, reposFolder
from utils import get_json_file_cls, myprint, Command
import config as conf


class Commit:

    def __init__(self):
        self.repos: List[RepoInfo] = get_json_file_cls(checkoutResult, RepoInfo)

    # git commit -am "<commit message>"
    def commitRepos(self):
        for repo in self.repos:
            repo_path = os.path.abspath(os.path.join(reposFolder, repo.repo_short))
            myprint("Committing changes to repo " + repo.repo_short + " at " + repo_path, 2)
            msg = "Commit made by release scripts for release: "+str(conf.release_name)
            Command(['git', '--work-tree', repo_path, 'commit', '-am', msg])

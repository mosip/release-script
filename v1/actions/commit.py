import os
from typing import List

from classes.repoInfo import RepoInfo
from paths import checkoutResult, reposFolder
from utils import get_json_file_cls, myprint, Command, getGitDirAndWorkTree
import config as conf


class Commit:

    def __init__(self):
        self.repos: List[RepoInfo] = get_json_file_cls(checkoutResult, RepoInfo)

    # git commit -am "<commit message>"
    def commitRepos(self):
        for repo in self.repos:
            git_dir, work_tree = getGitDirAndWorkTree(repo.repo_path)
            myprint("Committing changes to repo " + repo.repo_short + " at " + repo.repo_path, 2)
            msg = "Commit made by release scripts for release: "+str(conf.release_name)
            Command(['git', git_dir, work_tree, 'commit', '-am', msg], True)

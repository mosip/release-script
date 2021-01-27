import os
from typing import List

from classes.repoInfo import RepoInfo
from paths import checkoutResult, releaseUrlUpdateResult
from utils import get_json_file_cls, myprint, Command, getGitDirAndWorkTree, write_json_file, readFileAsString, match, \
    writeFileFromString
import config as conf


class ReleaseUrlUpdate:

    def __init__(self):
        self.repos: List[RepoInfo] = get_json_file_cls(checkoutResult, RepoInfo)

    def checkTriggers(self):
        output = []
        for repo in self.repos:
            info = self.checkTrigger(repo)
            repo.set_trigger_info(info)
            output.append(repo.__dict__)
        write_json_file(releaseUrlUpdateResult, output)

    def checkTrigger(self, repo):
        myprint('Checking push trigger info for repo: ' + repo.repo, 2)
        info = []
        push_trigger_path = os.path.join(repo.repo_path, conf.push_trigger_path)
        if os.path.exists(push_trigger_path) and os.path.isfile(push_trigger_path):
            myprint("Push trigger found: " + push_trigger_path)
            data = readFileAsString(push_trigger_path)
            if match(conf.release_repo_identifier, data):
                myprint("release_repo_identifier found")
                info.append("release_repo_identifier found")

                myprint("Replacing the release url")
                data = data.replace(conf.release_repo_identifier, conf.release_artifactory_url)
                writeFileFromString(push_trigger_path, data)
            else:
                myprint("release_repo_identifier not found")
                info.append("release_repo_identifier not found")
        else:
            myprint("Push trigger not found: " + push_trigger_path)
            info.append("Push trigger not found: " + push_trigger_path)
        return info
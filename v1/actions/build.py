from typing import List

from actions.common import getAllPoms, checkIfParentPom
from classes.repoInfo import RepoInfo
from paths import checkoutResult
from utils import get_json_file_cls, myprint, Command
import config as conf


class Build:

    def __init__(self):
        self.repos: List[RepoInfo] = get_json_file_cls(checkoutResult, RepoInfo)

    def build(self):
        for repo in self.repos:
            myprint('Preparing to build repo: ' + repo.repo, 2)
            myprint('Finding parent pom', 3)
            parent_poms, all_poms = self.findPoms(repo)
            if len(parent_poms) == 0:
                myprint('No Parent pom found')
                for pom in all_poms:
                    self.mvnInstall(pom)
            else:
                for pom in parent_poms:
                    myprint('Building parent pom '+pom)
                    self.mvnInstall(pom)

    def findPoms(self, repo):
        parent_poms = []
        poms = getAllPoms(repo)
        for pom in poms:
            is_parent = checkIfParentPom(pom)
            if is_parent:
                myprint('Parent pom found: '+pom)
                parent_poms.append(pom)
        return parent_poms, poms

    def mvnInstall(self, pom):
        if conf.maven_skip_tests:
            Command(['mvn', 'clean', 'install', '-f', pom, '-Dgpg.skip=true', '-Dmaven.test.skip=true'])
        else:
            Command(['mvn', 'clean', 'install', '-f', pom, '-Dgpg.skip=true'])
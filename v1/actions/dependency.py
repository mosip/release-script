import re
from pathlib import Path

import xml.etree.ElementTree as eT
from typing import List

from actions.common import getAllPoms, getPropertiesFromPom, updatePropertiesInPom, isMosipDep, getVersionsFromPom, \
    updateVersionsInPom
from classes.pomProperty import PomProperty
from classes.repoInfo import RepoInfo
from paths import checkoutResult, depCheckResult, depCheckDetailedResult, depUpdateResult
from utils import get_json_file, myprint, write_json_file, get_json_file_cls
import config as conf


class Dependency:

    def __init__(self):
        self.repos: List[RepoInfo] = get_json_file_cls(checkoutResult, RepoInfo)

    def pomCheck(self):
        output = []
        output_detailed = []
        for repo in self.repos:
            is_outdated = self.propertiesCheck(repo)
            is_outdated = is_outdated if is_outdated else self.versionCheck(repo)

            repo.set_is_pom_outdated(is_outdated)

            output_detailed.append(repo.__dict__)
            write_json_file(depCheckDetailedResult, output)

            repo.set_pom_info([])
            output.append(repo.__dict__)
            write_json_file(depCheckResult, output)

    def propertiesCheck(self, repo):
        myprint('Checking pom properties for repo: ' + repo.repo, 2)
        pom_info = []
        pom_stats = []
        paths = getAllPoms(repo)
        is_overall_outdated = False
        for p in paths:
            myprint('Checking ' + p, 3)
            pom_properties: List[PomProperty] = getPropertiesFromPom(p)
            is_outdated, stats, info = self.verifyDeps(pom_properties)
            pom_info.append({'name': p, 'info': info})
            pom_stats.append({'name': p, 'stats': stats})
            is_overall_outdated = is_overall_outdated if is_overall_outdated else is_outdated

        if is_overall_outdated:
            myprint('Outdated dependencies found', 11)
        else:
            myprint('No Outdated dependencies', 12)

        # Short report
        repo.set_pom_stats(pom_stats)

        # Detailed report
        repo.set_pom_info(pom_info)

        return is_overall_outdated

    def versionCheck(self, repo: RepoInfo):
        myprint('Checking pom version for repo: ' + repo.repo, 2)
        paths = getAllPoms(repo)
        is_outdated = False
        for p in paths:
            myprint('Checking ' + p, 3)
            module_version, parent_version = getVersionsFromPom(p)
            if module_version == conf.release_name:
                myprint('Module version is correct')
            else:
                is_outdated = True
                myprint('Outdated module version')

            if parent_version is None or parent_version == conf.release_name:
                myprint('Parent version is correct')
            else:
                is_outdated = True
                myprint('Outdated parent version')

            if parent_version is None:
                parent_version = 'No parent'

        repo.set_parent_poms({'module_version': module_version, 'parent_version': parent_version})
        return is_outdated

    def depUpdate(self):
        output = []
        for repo in self.repos:
            myprint('Updating pom dependencies for repo: ' + repo.repo, 2)
            pom_info = []
            pom_version_info = []
            paths = getAllPoms(repo)
            for p in paths:
                myprint('Updating ' + p, 3)
                res = updatePropertiesInPom(p, conf.release_name)
                pom_info.append({'name': p, 'info': res})

                res2 = updateVersionsInPom(p, conf.release_name)
                pom_version_info.append({'name': p, 'info': res2})
            repo.set_pom_info(pom_info)
            repo.set_parent_poms(pom_version_info)
            output.append(repo.__dict__)
        write_json_file(depUpdateResult, output)

    def verifyDeps(self, pom_properties: List[PomProperty]):
        is_outdated = False
        mosip_deps: List = []
        outdated: List = []
        updated: List = []
        total: List = []
        for prop in pom_properties:
            if isMosipDep(prop.name):
                mosip_deps.append(prop.__dict__)
                if prop.version == conf.release_name:
                    updated.append(prop.__dict__)
                else:
                    outdated.append(prop.__dict__)
            total.append(prop.__dict__)
        if len(outdated) > 0:
            is_outdated = True
        myprint('Total deps: ' + str(len(pom_properties)))
        myprint('MOSIP deps: ' + str(len(mosip_deps)))
        myprint('MOSIP updated deps: ' + str(len(updated)))
        myprint('MOSIP outdated deps: ' + str(len(outdated)))
        stats = {'mosip_outdated': len(outdated), 'mosip_updated': len(updated), 'mosip_deps': len(mosip_deps),
                 'total': len(pom_properties)}
        return is_outdated, stats, {'mosip_outdated': outdated, 'mosip_updated': updated, 'mosip_deps': mosip_deps,
                                    'total': total}

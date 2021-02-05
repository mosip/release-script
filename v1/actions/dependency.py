import copy
import re
from pathlib import Path

import xml.etree.ElementTree as eT
from typing import List

from actions.common import getAllPoms, isMosipDep, getVersionsFromPom, \
    isMosipProp, getCombined, updateVersions, updateProperty, updateDependency
from classes.pomProperty import PomProperty
from classes.repoInfo import RepoInfo
from paths import checkoutResult, depCheckResult, depCheckDetailedResult, depUpdateResult
from classes.pomDependency import PomDependency
from utils import get_json_file, myprint, write_json_file, get_json_file_cls
import config as conf


class Dependency:

    def __init__(self):
        self.repos: List[RepoInfo] = get_json_file_cls(checkoutResult, RepoInfo)

    def pomCheck(self):
        output = []
        output_detailed = []
        is_outdated = False
        for repo in self.repos:
            myprint('Checking repo ' + repo.repo, 2)
            pom_stats = []
            pom_info = []
            paths = getAllPoms(repo)
            for p in paths:
                myprint('Checking pom ' + p, 3)
                mosip_deps = []
                mosip_deps_outdated = []
                mosip_deps_updated = []

                pom_version, pom_properties, pom_dependencies = getCombined(p)
                total_deps = len(pom_dependencies)

                myprint('Checking version')
                if pom_version.parent is not None:
                    if pom_version.parent != conf.release_name:
                        myprint('POM parent version is outdated', 11)
                        is_outdated = True
                if pom_version.module != conf.release_name:
                    myprint('POM module version is outdated', 11)
                    is_outdated = True

                myprint('Checking dependencies')
                for deps in pom_dependencies:
                    if isMosipDep(deps.group_id):
                        mosip_deps.append(deps.__dict__)
                        dep_version = self.getDepVersion(deps, pom_properties)
                        if dep_version != conf.release_name:
                            myprint('Dependency ' + deps.artifact_id + ' is outdated, current version ' + dep_version,
                                    11)
                            is_outdated = True
                            mosip_deps_outdated.append(deps.__dict__)
                        else:
                            mosip_deps_updated.append(deps.__dict__)

                pom_stats.append({
                    'pom': p,
                    'stats': {
                        'mosip_deps_total': len(mosip_deps),
                        'mosip_deps_outdated': len(mosip_deps_outdated),
                        'mosip_deps_updated': len(mosip_deps_updated),
                        'total_deps': total_deps
                    }
                })
                pom_info.append({
                    'pom': p,
                    'stats': {
                        'mosip_deps_total': mosip_deps,
                        'mosip_deps_outdated': mosip_deps_outdated,
                        'mosip_deps_updated': mosip_deps_updated,
                    }
                })
            repo.set_pom_stats(pom_stats)
            repo.set_is_pom_outdated(is_outdated)
            output.append(copy.deepcopy(repo).__dict__)

            repo.set_pom_info(pom_info)
            output_detailed.append(repo.__dict__)
        write_json_file(depCheckDetailedResult, output_detailed)
        write_json_file(depCheckResult, output)

    def pomUpdate(self):
        output = []
        for repo in self.repos:
            myprint('Checking repo ' + repo.repo, 2)
            pom_info = []
            paths = getAllPoms(repo)
            for p in paths:
                info = []
                myprint('Checking pom ' + p, 3)
                pom_version, pom_properties, pom_dependencies = getCombined(p)
                myprint('Checking version')
                if pom_version.parent is not None:
                    if pom_version.parent != conf.release_name:
                        myprint(
                            'Updating pom parent version, old parent version ' + pom_version.module + ', '
                                                                                                      'new parent '
                                                                                                      'version ' +
                            conf.release_name
                            , 11)
                        updateVersions(p, conf.release_name)
                if pom_version.module != conf.release_name:
                    myprint(
                        'Updating pom module version, old module version ' + pom_version.module + ', new module '
                                                                                                  'version ' +
                        conf.release_name,
                        11)
                    updateVersions(p, conf.release_name)

                myprint('Checking dependencies')
                for deps in pom_dependencies:
                    if isMosipDep(deps.group_id):
                        dep_version = self.getDepVersion(deps, pom_properties)
                        if dep_version != conf.release_name:
                            out = self.updateDepVersion(p, deps, pom_properties)
                            info.append(out)
                pom_info.append({'pom': p, 'info': info})
            repo.set_pom_info(pom_info)
            output.append(repo.__dict__)
        write_json_file(depUpdateResult, output)

    def getDepVersion(self, dep: PomDependency, properties: List[PomProperty]):
        if '${' in dep.version.strip():
            prop_name = re.sub('[${}]', '', dep.version)
            for prop in properties:
                if prop.name == prop_name:
                    return prop.version
            raise RuntimeError(
                "Version not found for dependency: " + dep.group_id + ":" + dep.artifact_id + ":" + dep.version)
        else:
            return dep.version

    def updateDepVersion(self, path, dep: PomDependency, properties: List[PomProperty]):
        if '${' in dep.version.strip():
            prop_name = re.sub('[${}]', '', dep.version)
            for prop in properties:
                if prop.name == prop_name:
                    return updateProperty(path, prop_name, conf.release_name)
            raise RuntimeError(
                "Version not found for dependency: " + dep.group_id + ":" + dep.artifact_id + ":" + dep.version)
        else:
            return updateDependency(path, dep.group_id, dep.artifact_id, conf.release_name)

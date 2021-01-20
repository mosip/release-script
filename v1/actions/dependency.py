import re
from pathlib import Path

import xml.etree.ElementTree as eT
from typing import List

from classes.pomProperty import PomProperty
from classes.repoInfo import RepoInfo
from paths import checkoutResult, depCheckResult, depCheckDetailedResult
from utils import get_json_file, myprint, write_json_file, get_json_file_cls
import config as conf


class Dependency:

    def __init__(self):
        self.repos: List[RepoInfo] = get_json_file_cls(checkoutResult, RepoInfo)

    def depCheck(self):
        output = []
        output_detailed = []
        is_overall_outdated = False
        for repo in self.repos:
            pom_info = []
            pom_stats = []
            paths = self.getAllPoms(repo)
            for p in paths:
                pom_properties: List[PomProperty] = self.getPropertiesFromPom(p)
                is_outdated, stats, info = self.verifyDeps(pom_properties)
                pom_info.append({'name': p, 'info': info})
                pom_stats.append({'name': p, 'stats': stats})
                is_overall_outdated = is_overall_outdated if is_overall_outdated else is_outdated
            # Short report
            repo.set_is_pom_outdated(is_overall_outdated)
            repo.set_pom_stats(pom_stats)
            output.append(repo.__dict__)
            write_json_file(depCheckResult, output)

            # Detailed report
            repo.set_pom_info(pom_info)
            output_detailed.append(repo.__dict__)
            write_json_file(depCheckDetailedResult, output)

    def depUpdate(self):
        output = []
        output_detailed = []
        is_overall_outdated = False
        for repo in self.repos:
            pom_info = []
            pom_stats = []
            paths = self.getAllPoms(repo)
            for p in paths:
                pom_properties: List[PomProperty] = self.getPropertiesFromPom(p)

    def getAllPoms(self, repo):
        pth = []
        for path in Path(repo.repo_path).rglob('pom.xml'):
            pth.append(str(path.resolve()))
        return pth

    def getPropertiesFromPom(self, file) -> List[PomProperty]:
        pom_properties: List[PomProperty] = []
        tree = eT.parse(file)
        namespace = self.namespace(tree.getroot())
        for node in tree.findall(namespace + 'properties'):
            for props in node.getchildren():
                pom_properties.append(PomProperty(props.tag.replace(namespace, ''), props.text))
        return pom_properties

    def updatePropertiesInPom(self, input_file, version, output_file=None) -> List[PomProperty]:
        output = []
        pom_properties: List[PomProperty] = []
        tree = eT.parse(input_file)
        namespace = self.namespace(tree.getroot())
        eT.register_namespace('', self.namespaceUrl(tree.getroot()))
        for node in tree.findall(namespace + 'properties'):
            for pom_property in node.getchildren():
                pom_property_name = self.getElementName(pom_property)
                if self.isMosipDep(pom_property_name):
                    if pom_property.text != version:
                        output.append({'dependency': pom_property_name, 'previous_version': pom_property.text,
                                       'new_version': version})
                        pom_property.text = version
                pom_properties.append(PomProperty(pom_property.tag.replace(namespace, ''), pom_property.text))
        if output_file is not None:
            tree.write(output_file)
        else:
            tree.write(input_file)
        return output

    def namespace(self, element):
        m = re.match(r'\{.*\}', element.tag)
        return m.group(0) if m else ''

    def namespaceUrl(self, element):
        m = re.match(r'\{.*\}', element.tag)
        return m.group(0).replace('{', '').replace('}', '') if m else ''

    def getElementName(self, element):
        return element.tag.replace(self.namespace(element), '')

    def verifyDeps(self, pom_properties: List[PomProperty]):
        is_outdated = False
        mosip_deps: List = []
        outdated: List = []
        updated: List = []
        total: List = []
        for prop in pom_properties:
            if self.isMosipDep(prop.name):
                mosip_deps.append(prop.__dict__)
                if prop.version == conf.release_name:
                    updated.append(prop.__dict__)
                else:
                    outdated.append(prop.__dict__)
            total.append(prop.__dict__)
        if len(outdated) > 0:
            is_outdated = True
        stats = {'mosip_outdated': len(outdated), 'mosip_updated': len(outdated), 'mosip_deps': len(mosip_deps),
                 'total': len(pom_properties)}
        return is_outdated, stats, {'mosip_outdated': outdated, 'mosip_updated': updated, 'mosip_deps': mosip_deps,
                                    'total': total}

    def isMosipDep(self, dep):
        if conf.mosip_dep_match_regex is not None and isinstance(conf.mosip_dep_match_regex, list) and \
                len(conf.mosip_dep_match_regex) > 0:
            for reg in conf.mosip_dep_match_regex:
                m = re.match(reg, dep)
                res = True if m else False
                if res:
                    return res
            return False
        else:
            raise RuntimeError('Config variable (mosip_dep_match_regex) is required to match mosip dependencies')

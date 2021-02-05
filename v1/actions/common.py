import re
from _elementtree import Element
from pathlib import Path
from typing import List
from xml.dom import Node

from classes.pomProperty import PomProperty
import xml.etree.ElementTree as eT

from classes.pomDependency import PomDependency
from classes.pomVersion import PomVersion
from utils import myprint
import config as conf


def getAllPoms(repo):
    pth = []
    for path in Path(repo.repo_path).rglob('pom.xml'):
        pth.append(str(path.resolve()))
    return pth


def getCombined(file):
    pom_properties: List[PomProperty] = []
    pom_dependencies: List[PomDependency] = []
    tree = xmlToTree(file)
    namespace = getNamespace(tree.getroot())
    for node in tree.findall(namespace + 'properties'):
        for props in node.getchildren():
            pom_properties.append(PomProperty(props.tag.replace(namespace, ''), props.text))

    for node in tree.findall(namespace + 'dependencies'):
        # {groupId, artifactId, version}
        for deps in node.getchildren():
            pom_dependencies.append(getDependency(deps))

    pom_version = getVersionsFromPom(file)
    return pom_version, pom_properties, pom_dependencies


def updateVersions(input_file, version, output_file=None):
    output = []
    tree = xmlToTree(input_file)
    namespace = getNamespace(tree.getroot())
    eT.register_namespace('', namespaceUrl(tree.getroot()))
    for node in tree.findall(namespace + 'version'):
        pom_property_name = getElementName(node)
        myprint('child ' + pom_property_name + ': ' + node.text + ' -> ' + version)
        output.append({'module_previous_version': node.text,
                       'module_new_version': version})
        node.text = version
    for node in tree.findall(namespace + 'parent'):
        for props in node.getchildren():
            pom_property_name = getElementName(props)
            if getElementName(props) == 'version':
                myprint('parent ' + pom_property_name + ': ' + props.text + ' -> ' + version)
                output.append({'parent_previous_version': props.text, 'parent_new_version': version})
                props.text = version

    if output_file is not None:
        treeToXml(tree, output_file)
    else:
        treeToXml(tree, input_file)
    return output


def updateProperty(input_file, name, version, output_file=None):
    output = []
    tree = xmlToTree(input_file)
    namespace = getNamespace(tree.getroot())
    for node in tree.findall(namespace + 'properties'):
        for pom_property in node.getchildren():
            pom_property_name = getElementName(pom_property)
            if name == pom_property_name:
                if pom_property.text != version:
                    myprint(pom_property_name + ': ' + pom_property.text + ' -> ' + version)
                    output.append({'property': pom_property_name, 'previous_version': pom_property.text,
                                   'new_version': version})
                    pom_property.text = version
    if output_file is not None:
        treeToXml(tree, output_file)
    else:
        treeToXml(tree, input_file)
    return output


def updateDependency(input_file, group, artifact, version, output_file=None):
    output = []
    tree = xmlToTree(input_file)
    namespace = getNamespace(tree.getroot())
    for node in tree.findall(namespace + 'dependencies'):
        for deps in node.getchildren():
            dep = getDependency(deps)
            if group == dep.group_id and artifact == dep.artifact_id:
                if dep.version != version:
                    for element in deps.getchildren():
                        tag = element.tag.replace(getNamespace(element), '')
                        if tag == 'version':
                            myprint(dep.artifact_id + ': ' + dep.version + ' -> ' + version)
                            output.append({'dependency': dep.group_id+":"+dep.artifact_id, 'previous_version': dep.version,
                                           'new_version': version})
                            element.text = version
    if output_file is not None:
        treeToXml(tree, output_file)
    else:
        treeToXml(tree, input_file)
    return output


def getVersionsFromPom(file) -> PomVersion:
    module_version = None
    parent_version = None
    tree = xmlToTree(file)
    namespace = getNamespace(tree.getroot())
    for node in tree.findall(namespace + 'version'):
        myprint('child version: ' + node.text)
        module_version = node.text
    for node in tree.findall(namespace + 'parent'):
        for props in node.getchildren():
            if getElementName(props) == 'version':
                myprint('parent version: ' + props.text)
                parent_version = props.text
    return PomVersion(module_version, parent_version)


def getDependency(element_obj: Node) -> PomDependency:
    group_id = None
    artifact_id = None
    version = None
    if element_obj is not None:
        for element in element_obj.getchildren():
            tag = element.tag.replace(getNamespace(element), '')
            if tag == 'groupId':
                group_id = element.text
            if tag == 'artifactId':
                artifact_id = element.text
            if tag == 'version':
                version = element.text
    return PomDependency(group_id, artifact_id, version)


def getNamespace(element):
    m = re.match(r'\{.*\}', element.tag)
    return m.group(0) if m else ''


def namespaceUrl(element):
    m = re.match(r'\{.*\}', element.tag)
    return m.group(0).replace('{', '').replace('}', '') if m else ''


def getElementName(element):
    return element.tag.replace(getNamespace(element), '')


def isMosipProp(dep):
    if conf.mosip_property_match_regex is not None and isinstance(conf.mosip_property_match_regex, list) and \
            len(conf.mosip_property_match_regex) > 0:
        for reg in conf.mosip_property_match_regex:
            m = re.match(reg, dep)
            res = True if m else False
            if res:
                return res
        return False
    else:
        raise RuntimeError('Config variable (mosip_property_match_regex) is required to match mosip dependencies')


def isMosipDep(dep):
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


def checkIfParentPom(file):
    tree = eT.parse(file)
    namespace = getNamespace(tree.getroot())
    for node in tree.findall(namespace + 'artifactId'):
        m = re.match(r'.*parent', node.text)
        return True if m else False


def xmlToTree(file):
    tree = eT.parse(file)
    eT.register_namespace('', namespaceUrl(tree.getroot()))
    return tree


def treeToXml(tree, file):
    tree.write(file)
import re
from pathlib import Path
from typing import List

from classes.pomProperty import PomProperty
import xml.etree.ElementTree as eT

from utils import myprint
import config as conf


def getAllPoms(repo):
    pth = []
    for path in Path(repo.repo_path).rglob('pom.xml'):
        pth.append(str(path.resolve()))
    return pth


def getPropertiesFromPom(file) -> List[PomProperty]:
    pom_properties: List[PomProperty] = []
    tree = xmlToTree(file)
    namespace = getNamespace(tree.getroot())
    for node in tree.findall(namespace + 'properties'):
        for props in node.getchildren():
            pom_properties.append(PomProperty(props.tag.replace(namespace, ''), props.text))
    return pom_properties


def updatePropertiesInPom(input_file, version, output_file=None) -> List[PomProperty]:
    output = []
    pom_properties: List[PomProperty] = []
    tree = xmlToTree(input_file)
    namespace = getNamespace(tree.getroot())
    for node in tree.findall(namespace + 'properties'):
        for pom_property in node.getchildren():
            pom_property_name = getElementName(pom_property)
            if isMosipDep(pom_property_name):
                if pom_property.text != version:
                    myprint(pom_property_name + ': ' + pom_property.text + ' -> ' + version)
                    output.append({'dependency': pom_property_name, 'previous_version': pom_property.text,
                                   'new_version': version})
                    pom_property.text = version
            pom_properties.append(PomProperty(pom_property.tag.replace(namespace, ''), pom_property.text))
    if output_file is not None:
        treeToXml(tree, output_file)
    else:
        treeToXml(tree, input_file)
    return output


def getVersionsFromPom(file):
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
    return module_version, parent_version


def updateVersionsInPom(input_file, version, output_file=None) -> List[PomProperty]:
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


def getNamespace(element):
    m = re.match(r'\{.*\}', element.tag)
    return m.group(0) if m else ''


def namespaceUrl(element):
    m = re.match(r'\{.*\}', element.tag)
    return m.group(0).replace('{', '').replace('}', '') if m else ''


def getElementName(element):
    return element.tag.replace(getNamespace(element), '')


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
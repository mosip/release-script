import subprocess
import csv
import yaml
import sys
import json
from concurrent.futures import ProcessPoolExecutor
import concurrent
import requests
import string
import re
import logging
import os
from datetime import datetime

# Function to install Docker module
def install_docker_module():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "docker"])
    except subprocess.CalledProcessError:
        print("Error: Failed to install the Docker module.")
        sys.exit(1)

# Install Docker module
install_docker_module()

# Now import the Docker module
import docker as dock

config = {}


# def kick_start():
#    with concurrent.futures.ThreadPoolExecutor(max_workers=config['process']['count']) as executor:

def print_log(msg, loglevel):
    print(msg)
    if loglevel == 'debug':
        logging.debug(msg)
    if loglevel == 'info':
        logging.info(msg)
    if loglevel == 'error':
        logging.error(msg)
    if loglevel == 'critical':
        logging.critcal(msg)
    if loglevel == 'warning':
        logging.warning(msg)
    return


def chkImagesList(images):
    # set src image and dest image with tag
    filtered_images = [[i for i in image if i != ''] for image in images if image != '']
    images_list=[]
    for image in filtered_images:
        for i in image:
            if len(image)<2:
                j=i.split("\t")
                images_list.append([img for img in j if img != ''])
            else:
                if image not in images_list:
                    images_list.append(image)
                    continue

    print("image_list = ",[i for i in images_list])
    images = []
    tagsNotAvailable = []
    for image in images_list:
        colon_index = image[0].find(":")
        if colon_index > -1:
            if len(image[0]) - 1 == colon_index:
                print_log('Image "' + image[0] + '" with tag doesn\'t exists', 'error')
                tagsNotAvailable.append(image[0])
                continue
            if len(image) == 1:
                image = [image[0]] + [image[0][colon_index + 1:]]
            images.append(image)
        if colon_index == -1:
            if len(image) == 1:
                print_log('Image "' + image[0] + '" with tag doesn\'t exists', 'error')
                tagsNotAvailable.append(image[0])
                continue
            if len(image) == 2:
                image = [image[0] + ':' + image[1]] + [image[1]]
            images.append(image)

    return images, tagsNotAvailable


def chkImageExistence(image, tag, registry_url):
    if '@sha256:' in image:
        image_name, image_digest = image.split('@sha256:')
        url = registry_url + "repositories/" + image_name + "/manifests/" + "sha256:" + image_digest
    else:
        url = registry_url + "repositories/" + image + "/tags/" + tag
    print("url= " + url)
    r = requests.get(url=url)
    # If image not found exit the script
    if int(r.status_code) == 404:
        print_log("Image \"" + image + ":" + tag + "\" does not exist", 'error')
        return False
    return True


def ignoreComment(csvfile):
    for row in csvfile:
        raw = row.split('#')[0].strip()
        if raw: yield raw


def getDockerHash(repo, tag):
    url = 'https://auth.docker.io/token?service=registry.docker.io&scope=repository:' + repo + ':pull'
    token_req = requests.get(url=url, headers={"Content-Type": "text"})
    token = token_req.json()['token']
    headers = {
        "Accept": "application/vnd.docker.distribution.manifest.v2+json",
        "Authorization": "Bearer " + token + ""
    }
    registryUrl = 'https://registry-1.docker.io/v2/' + repo + '/manifests/' + tag + ''
    getImageHash = requests.get(registryUrl, headers=headers)
    if getImageHash.status_code == 200:
        return getImageHash.headers['etag']
    return ''


def chkDockerAccExistence(acc_name):
    accUrl = 'https://hub.docker.com/v2/users/' + acc_name
    req = requests.get(url=accUrl)
    if int(req.status_code) == 404:
        print_log("Docker account with Name " + acc_name + " does not exists", 'error')
        return False
    return True


def main():
    client = dock.from_env()
    registry_url = "https://index.docker.io/v1/"
    # create log file with format date-time.log
    if not os.path.exists('./logs/'):
        os.makedirs('./logs/')
    logFile = "vidivi-" + datetime.now().strftime("%d-%m-%Y-%H:%M:%S") + ".log"
    logging.basicConfig(filename='logs/' + logFile, level=logging.DEBUG, filemode='a',
                        format=' %(asctime)s  %(levelname)s  %(message)s ',
                        datefmt='%d-%b-%y %H:%M:%S')
    print_log('LOGFILE CREATED : ' + logFile, 'info')

    header = config['csv']['has_header']
    with open(config['csv']['filename'], newline='') as image_data:
        images = csv.reader(ignoreComment(image_data), delimiter=' ')
        # calling chkImagesList function
        print_log("", 'info')
        print_log('*' * 20 + " Check Images List " + '*' * 84, 'info')
        images, tagsNotAvailable = chkImagesList(images)
        print_log("", 'info')
        print_log("IMAGES= " + str(images), 'info')
    if len(tagsNotAvailable) > 0:
        print_log("", 'info')
        print_log("Tag not provided for the images list below: \n\t" + str(tagsNotAvailable) + "", 'error')
        exit(1)
        
    # check the existence of srcImage+tag
    print_log("", 'info')
    print_log('*' * 20 + " Check existence of Source Images " + '*' * 67, 'info')
    srcImgNotExist = []
    srcDestSameImg = []
    destImgNotExist = []
    srcDestNotSameHash = []
    srcDestSameHash = []
    for image in images:
        srcImgName = image[0][: image[0].find(":")]
        srcImgtag = image[0][image[0].find(":") + 1:]
        print_log("", 'info')
        print_log("src = \"" + srcImgName + "\" tag = \"" + srcImgtag + "\"", 'info')
        # call function to check existence of source images
        if not chkImageExistence(srcImgName, srcImgtag, registry_url):
            srcImgNotExist.append([srcImgName + ":" + srcImgtag])
        # check if source and destination images are same
        destImgName = config['docker']['destination_organization'] + "/" + (srcImgName.split('/')[-1])
        destImgtag = image[1]
        if destImgName == srcImgName and destImgtag == srcImgtag:
            srcDestSameImg.append([destImgName, destImgtag])
    # print list of source images which does not exist
    if len(srcImgNotExist) > 0:
        print_log("", 'info')
        print_log("Below Source Images doesn't exists; EXITING;\n\t" + str(srcImgNotExist), 'error')
        exit(1)
    # print list of same source and destination images
    if len(srcDestSameImg) > 0:
        print_log("", 'info')
        print_log("Below list consist of same source and destination images; EXITING;\n\t" + str(srcDestSameImg),
                  'error')
        exit(1)

    # stop if user passed is equal to 'check' as an argument
    if sys.argv[1] == "check":
        print_log("", 'info')
        print_log("Operation to check the existence of Source Images completed; EXITING;", 'info')
        exit(0)

    # check the existence of destImg+tag
    print_log("", 'info')
    print_log('*' * 20 + " Check existence of Destination Docker Account " + '*' * 63, 'info')
    if not chkDockerAccExistence(config['docker']['destination_organization']):
        exit(1)
    print_log("", 'info')
    print_log('*' * 20 + " Check existence of Destination Images " + '*' * 63, 'info')
    for image in images:
        imgName = image[0][: image[0].find(":")]
        destImgName = config['docker']['destination_organization'] + "/" + (imgName.split('/')[-1])
        destImgTag = image[1]
        destImgHash = getDockerHash(destImgName, destImgTag)
        print_log("", 'info')
        print_log("[ " + destImgName + " ] ", 'info')
        print_log("Destination Image = \"" + destImgName + "\" Destination Image tag = \"" + str(destImgTag) + "\" IMAGE_ID : " + destImgHash, 'info')
        
        # call function to check existence of destination images
        if not chkImageExistence(destImgName, destImgTag, registry_url):
            destImgNotExist.append([destImgName + ":" + destImgTag])
            continue

        # compare only when performing hash operation
        if sys.argv[1] == "hash":
            srcImgHash = getDockerHash(imgName, image[0][image[0].find(":") + 1:])
            destImgHash = getDockerHash(destImgName, destImgTag)

            if srcImgHash != destImgHash:
                print_log("", 'info')
                print_log("Source Image = \"" + image[0] + "\" IMAGE_ID :" + str(srcImgHash), 'info')
                print_log(
                    "Destination Image = \"" + destImgName + ":" + destImgTag + "\" IMAGE_ID :" + str(destImgHash),
                    'info')
                print_log("does not have same HASH ID ", 'info')
                srcDestNotSameHash.append(
                    {"srcImg": image[0], "srcImgHash": srcImgHash, "destImg": destImgName + ":" + destImgTag,
                     "destImgHash": destImgHash})
                continue

            print_log("", 'info')
            print_log("Source Image = \"" + image[0] + "\" IMAGE_ID :" + str(srcImgHash), 'info')
            print_log("Destination Image = \"" + destImgName + ":" + destImgTag + "\"IMAGE_ID : " + destImgHash, 'info')
            print_log("does have same HASH ID ", 'info')
            srcDestSameHash.append(
                {"srcImg": image[0], "srcImgHash": srcImgHash, "destImg": destImgName + ":" + destImgTag,
                 "destImgHash": destImgHash})

    print_log("", 'info')
    print_log('*' * 20 + " HASH Operation Results " + '*' * 70, 'info')
    if len(destImgNotExist) > 0:
        print_log("", 'info')
        print_log("Below Destination Images doesn't exists; CONTINUE;\n\t" + str(destImgNotExist), 'info')
    if len(srcDestNotSameHash) > 0:
        print_log("", 'info')
        print_log("Below List of Images does not contains same HASH / IMAGE ID \n\t" + str(srcDestNotSameHash), 'info')
    if len(srcDestSameHash) > 0:
        print_log("", 'info')
        print_log("Below List of Images does contains same HASH / IMAGE ID \n\t" + str(srcDestSameHash), 'info')

    # stop if user passed is not 'push' as an argument
    if sys.argv[1] != "push":
        print_log("", 'info')
        print_log("Check and HASH operation completed; EXITING;", 'info')
        exit(0)

    print_log("", 'info')
    print_log('*' * 20 + " Start Image Transfer operation " + '*' * 71, 'info')
    remote_client = dock.APIClient(base_url='unix:///var/run/docker.sock', version='auto')
    remote_client.login(username=config['docker']['username'], password=config['docker']['token'],
                        registry=config['docker']['registry_url'])
    for image in images:
        # start image transfer operation for src_repo/src_image_name:tag
        srcImgRepo = image[0][: image[0].find("/")]
        srcImgName = image[0][image[0].find("/") + 1:image[0].find(":")]
        srcImgtag = image[0][image[0].find(":") + 1:]
        destImgtag = image[1]
        print_log("", 'info')
        print_log(10 * "*" + " [ " + config['docker']['destination_organization'] + "/" + srcImgName + ":" + destImgtag + " ] " + "*" * 52, 'info')
        promote(srcImgRepo, srcImgName, srcImgtag, destImgtag, config['docker']['destination_organization'],
                remote_client, client)


def load_config():
    global config
    with open("config.yml", "r") as configfile:
        config = yaml.safe_load(configfile)


def strip_tag(image_name):
    image_version = ""
    stripped_list = image_name[0].split('/')
    repository = stripped_list[0]
    image = stripped_list[1]
    image_version = image_name[1]
    return repository, image, image_version


def promote(src_repo, src_image_name, src_image_version, tag, dst_repo, remote_client, local_client):
    src_repository = src_repo + "/" + src_image_name
    src_tag = tag if src_image_version == "" else src_image_version
    src_image = src_repository + ":" + src_tag
    force = True
    dst_repository = dst_repo + "/" + src_image_name
    dst_tag = tag
    dst_image = dst_repository + ":" + dst_tag
    dst_latest = dst_repository + ":" + "latest"
    if '@sha256:' in dst_image:
        #src_image = re.sub(r'@sha256','',src_image)
        dst_image = re.sub(r'@sha256','',dst_image)
        dst_repository = re.sub(r'@sha256','',dst_repository)
    print_log("", 'info')
    src_tag=':'+src_tag
    if '@sha256:' in src_image:
        #src_image = re.sub(r'@sha256','',src_image)
        src_repository = re.sub(r'@sha256','',src_repository)
        src_tag='@sha256'+src_tag
    print_log("[ PULL ----------------------> " + src_image + " ] ", 'info')
    print("src_repository : ",src_repository,'src_tag',src_tag, 'src_image : ',src_image )
    print('dst_repository : ',dst_repository, 'dst_tag : ', dst_tag)
    pull_status = remote_client.pull(repository=src_repository+src_tag, stream=True, decode=True)
    status_update(pull_status)
    remote_client.tag(image=src_image, repository=dst_repository, tag=dst_tag, force=force)
    print_log("", 'info')
    print_log("[ PUSH -----> " + src_image + "\t------> " + dst_image + " ] ", 'info')
    push_status = remote_client.push(repository=dst_repository, tag=dst_tag, stream=True, decode=True)
    status_update(push_status)
    print_log("", 'info')
    print_log("[ PUSH -----> " + src_image + "\t------> " + dst_latest + " ] ", 'info')
    remote_client.tag(image=src_image, repository=dst_repository, tag='latest', force=force)
    latest_push = remote_client.push(repository=dst_repository, tag='latest', stream=True, decode=True)
    status_update(latest_push)
    # remove docker images from local machine
    rm_local_img = [src_image, dst_image, dst_latest]
    for img in rm_local_img:
        if len(local_client.images.list(img)) != 0:
            local_client.images.remove(img)
    print_log("Completed " + src_image + "\t------> " + dst_image, 'info')


def status_update(output):
    status = ''
    for line in output:
        if line.get("error"):
            raise InterruptedError(line.get("error"))
        if line.get("progress"):
            print(line.get("status"), line.get("progress"), end="\r")
            # print(json.dumps(line, indent=4))
        if line.get('status'):
            status = line.get('status')
    # print("")
    print_log(status, 'info')


if __name__ == "__main__":
    if len(sys.argv[1:]) == 0:
        print_log("check / hash / push operation not passed as an argument; EXITING;", 'error')
        exit(1)
    if sys.argv[1] != "check" and sys.argv[1] != "push" and sys.argv[1] != "hash":
        print_log("INVALID operation provided; EXITING;", 'error')
        exit(1)

    load_config()

    if not config['docker']['destination_organization']:
        print_log("Destination Organization name not provided in config.yml; EXITING;", 'error')
        exit(1)
    main()

import docker as dock
import csv
import yaml
import sys
import json
from concurrent.futures import ProcessPoolExecutor
import concurrent
import requests
import string
import re

config = {}

#def kick_start():
#    with concurrent.futures.ThreadPoolExecutor(max_workers=config['process']['count']) as executor:

def chkImageExistence(images):
    imageList=list()
    for image in images:
        # check if list is empty
        #if (len(image)==0):
        #    print("List empty skipping")
        #    continue

        # remove empty values from list
        image=[ i.strip() for i in image if i!='' ]

        # change if
        if (len(image)!=2):
            image=[j for i in image  for j in i.split("\t") if j !='' ]

        image=[i.split(':') for i in image]

        # set url to check the existence of docker image
        if ( len(image[0]) == 1 ):
           url="https://index.docker.io/v1/repositories/"+image[0][0]+"/tags/"+image[1][0]
           image[0].insert(1,image[1][0])
        else:
           url="https://index.docker.io/v1/repositories/"+image[0][0]+"/tags/"+image[0][-1]
        print("url= "+url)
        r=requests.get(url=url)
        # If image not found exit the script
        # print(type(r.status_code))
        if ( int(r.status_code) == 404 ):
            print("Image "+image[0][0]+":"+image[0][-1]+" does not exists")
            exit(1)
        imageList.append(image)
    return imageList

def decomment(csvfile):
    for row in csvfile:
        raw = row.split('#')[0].strip()
        if raw: yield raw

def main():
    client = dock.from_env()
    remote_client = dock.APIClient(base_url='unix:///var/run/docker.sock', version='auto')
    registry_url="https://index.docker.io/v1/"
    
    remote_client.login(username=config['docker']['username'],password=config['docker']['token'],registry=config['docker']['registry_url'])
    header = config['csv']['has_header']
    with open(config['csv']['filename'], newline='') as image_data:
        images=csv.reader(decomment(image_data), delimiter=' ')
        print("\n"+'*'*20 +" Check existence of source Image "+'*'*70)
        imageList=chkImageExistence(images)
    print("\nImageList = "+str(imageList)+"\n")

    ##
    if ( sys.argv[1] == "check" ):
        exit(0);

    print("\n"+'*'*20 +" Start Image Transfer operation "+'*'*71)
    for image in imageList:
        if header == True:
           next(images)
           header = False
           continue
        image_name = ''
        tag = ''
        for item in image:
           if item == '':
              continue
           if image_name == '':
              image_name=item
           else:
              tag = item[0]
           if image_name == '':
              continue
        (src_repo, src_image_name, src_image_version) = strip_tag(image_name)
        # check if destination_tag is empty then set destination_tag=src_tag
        if (tag == ""):
           tag=src_image_version
        # start image transfer operation for src_repo/src_image_name:tag
        print("\n"+10*"*" +" [ "+ config['docker']['destination_organization']+"/"+src_image_name+":"+tag+ " ] "+"*"*52)
        promote(src_repo,src_image_name,src_image_version,tag,config['docker']['destination_organization'],remote_client,client)


def load_config():
    global config
    with open("config.yml", "r") as configfile:
        config = yaml.safe_load(configfile)

def strip_tag(image_name):
    image_version=""
    stripped_list = image_name[0].split('/')
    repository = stripped_list[0]
    image = stripped_list[1]
    image_version = image_name[1]
    return (repository,image,image_version)


def promote(src_repo, src_image_name, src_image_version, tag, dst_repo, remote_client, local_client):
    src_repository=src_repo+"/"+src_image_name
    src_tag = tag if src_image_version=="" else src_image_version
    src_image=src_repository+":"+src_tag
    force=True
    dst_repository=dst_repo+"/"+src_image_name
    dst_tag=tag
    dst_image=dst_repository+":"+dst_tag
    dst_latest=dst_repository+":"+"latest"
    print("Pull "+ src_image + "\t------> " + dst_image )
    pull_status = remote_client.pull(repository=src_repository, tag=src_tag, stream=True, decode=True)
    status_update(pull_status)
    remote_client.tag(image=src_image, repository=dst_repository, tag=dst_tag, force=force)
    print("Push "+ src_image + "\t------> " + dst_image )
    push_status=remote_client.push(repository=dst_repository, tag=dst_tag, stream=True, decode=True)
    status_update(push_status)
    print("Push "+ src_image + "\t------> " + dst_repository+":"+'latest' )
    remote_client.tag(image=src_image, repository=dst_repository, tag='latest', force=force)
    latest_push = remote_client.push(repository=dst_repository, tag='latest', stream=True, decode=True)
    status_update(latest_push)
    # remove docker images from local machine
    rm_local_img=[src_image,dst_image,dst_latest]
    for img in rm_local_img:
        if (len(local_client.images.list(img)) != 0):
            local_client.images.remove(img)
    print("Completed "+ src_image + "\t------> " + dst_image )

def status_update(output):
    status=''
    for line in output:
        if line.get("error"):
            raise InterruptedError(line.get("error"))
        if line.get("progress"):
            print(line.get("status"), line.get("progress"), end="\r")                    
        #print(json.dumps(line, indent=4))
        if line.get('status'):
            status=line.get('status')
    #print("")    
    print(status)


if __name__ == "__main__":
    if ( len(sys.argv[1:]) == 0):
        print("check / push operation not passed as an argument; EXITING;")
        exit(1);
    if ( sys.argv[1] != "check" and sys.argv[1] != "push"  ):
        print("INVALID operation providedt; EXITING;")
        exit(1);
    load_config()
    main()

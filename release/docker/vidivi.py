import docker as dock
import csv
import yaml
import sys
import json
from concurrent.futures import ProcessPoolExecutor
import concurrent

config = {}

#def kick_start():
#    with concurrent.futures.ThreadPoolExecutor(max_workers=config['process']['count']) as executor:



def main():
    client = dock.from_env()
    remote_client = dock.APIClient(base_url='unix:///var/run/docker.sock', version='auto')
    registry_url="https://index.docker.io/v1/"
    
    remote_client.login(username=config['docker']['username'],password=config['docker']['token'],registry=config['docker']['registry_url'])
    header = config['csv']['has_header']
    with open(config['csv']['filename'], newline='') as image_data:
        images=csv.reader(image_data, delimiter='\t')
        for image in images:
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
                    tag = item
            if image_name == '':
                continue            
            (src_repo, src_image_name) = strip_tag(image_name)
            promote(src_repo,src_image_name,tag,config['docker']['destination_organization'],remote_client,client)


def load_config():
    global config
    with open("config.yml", "r") as configfile:
        config = yaml.load(configfile)


def strip_tag(image_name):
    stripped_list = image_name.split('/')
    repository = stripped_list[0]
    image = stripped_list[1]
    return (repository,image)

def promote(src_repo, src_image_name,tag,dst_repo, remote_client, local_client):
    src_repository=src_repo+"/"+src_image_name
    src_tag = tag
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
    local_client.images.remove(src_image)
    local_client.images.remove(dst_image)
    local_client.images.remove(dst_latest)
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
    load_config()
    main()
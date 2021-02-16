import errno
import json
import os
import sys
from typing import Dict
import config as conf
import requests

from utils import get_timestamp, read_token, myprint, print_response, response_to_dict, dict_to_json

sys.path.insert(0, '../')


class MosipSession:
    def __init__(self, server, user, pwd, appid='prereg', ssl_verify=True):
        self.server = server
        self.user = user
        self.pwd = pwd
        self.ssl_verify = ssl_verify
        self.token = self.authGetToken(appid, self.user, self.pwd)

    def authGetToken(self, appid, username, pwd):
        myprint("authenticate api called")
        url = '%s/v1/authmanager/authenticate/clientidsecretkey' % self.server
        ts = get_timestamp()
        j = {
            "id": "mosip.io.clientId.pwd",
            "metadata": {},
            "version": "1.0",
            "requesttime": ts,
            "request": {
                "appId": appid,
                "clientId": username,
                "secretKey": pwd
            }
        }
        if conf.debug:
            myprint("Request: "+dict_to_json(j))
        r = requests.post(url, json=j, verify=self.ssl_verify)
        resp = self.parseResponse(r)
        if conf.debug:
            myprint("Response: "+dict_to_json(resp))
        token = read_token(r)
        return token

    def addApplication(self, data: Dict):
        myprint("addApplication api called")
        url = '%s/preregistration/v1/applications' % self.server
        cookies = {'Authorization': self.token}
        ts = get_timestamp()
        j = {
            "id": "mosip.pre-registration.demographic.create",
            "request": {
                "langCode": "eng",
                "demographicDetails": {
                    "identity": data
                }
            },
            "requesttime": ts,
            "version": "1.0"
        }
        if conf.debug:
            myprint("Request: " + dict_to_json(j))
        r = requests.post(url, cookies=cookies, json=j, verify=self.ssl_verify)
        resp = self.parseResponse(r)
        if conf.debug:
            myprint("Response: "+dict_to_json(resp))
        return resp

    def bookAppointment(self, data: Dict):
        myprint("bookAppointment api called")
        url = '%s/preregistration/v1/appointment' % self.server
        cookies = {'Authorization': self.token}
        ts = get_timestamp()
        j = {
            "id": "mosip.pre-registration.booking.book",
            "request": {
                "bookingRequest": [data]
            },
            "requesttime": ts,
            "version": "1.0"
        }
        if conf.debug:
            myprint("Request: " + dict_to_json(j))
        r = requests.post(url, cookies=cookies, json=j, verify=self.ssl_verify)
        resp = self.parseResponse(r)
        if conf.debug:
            myprint("Response: "+dict_to_json(resp))
        return resp

    @staticmethod
    def parseResponse(r):
        if r.status_code != 200:
            raise RuntimeError("Request failed with status: "+str(r.status_code))
        if r.content is not None:
            res = json.loads(r.content)
            if res['response'] is None:
                raise RuntimeError(res['errors'])
            else:
                return res['response']

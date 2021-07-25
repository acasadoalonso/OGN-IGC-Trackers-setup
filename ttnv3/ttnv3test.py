#!/bin/python3
import sys
import json
import urllib.request, urllib.error, urllib.parse
import datetime
import time
import os
import uritemplate
import netparams as net
import requests 
# ------------------------------------ ##
# TheThingsNetwork (TTN) parameters
#
TTN_app_id     = "ogn"
TTN_dev_id     = "ogn123456"
TTN_devEui     = "0000CC50E3123456"
TTN_appEui     = "70B3D57ED0035895"
TTN_joinEui    = TTN_appEui 				# "70B3D57ED0035895"
TTN_appKey     = "ttn-account-v2.V4Z-WSzqhfR0FKiKFYu4VLgNEbxP9QluACwD1pSfwmE"
TTN_auth       = "Bearer NNSXS.KWEZ5MIJBWBT36UYOIGDOW6WT6ECNJEI3Z5EODY.P4D4MVHM6HESSR6ZN4ITYONQCMIO4AD72AJPPUXK4IJ4NJPFGGOQ" 
TTNV3_appKey   = "KWEZ5MIJBWBT36UYOIGDOW6WT6ECNJEI3Z5EODY.P4D4MVHM6HESSR6ZN4ITYONQCMIO4AD72AJPPUXK4IJ4NJPFGGOQ" 
##################################################################


def getapidata(url, auth):                  # get the data from the API server

    req = urllib.request.Request(url)
    req.add_header('Authorization', auth)   # build the authorization header
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", " my-integration/my-integration-version")
    r = urllib.request.urlopen(req)         # open the url resource
    j_obj = json.load(r)                    # convert to JSON
    return j_obj                            # return the JSON object

##################################################################
#

auth="Bearer NNSXS.KWEZ5MIJBWBT36UYOIGDOW6WT6ECNJEI3Z5EODY.P4D4MVHM6HESSR6ZN4ITYONQCMIO4AD72AJPPUXK4IJ4NJPFGGOQ" 
#url= "https://eu1.cloud.thethings.network/api/v3/applications"
#url= "https://eu1.cloud.thethings.network/api/v3/applications/ogn"
url= "https://eu1.cloud.thethings.network/api/v3/applications/ogn/devices"
#url= "https://eu1.cloud.thethings.network/api/v3/applications/ogn/devices/ognc30734"
###############################################################################################
adddevice = {
  "ids": {
    "device_id": "ogn123456",
    "application_ids": {
      "application_id": "ogn"
    },
    "dev_eui": "0000CC50E3123456",
    "join_eui": "70B3D57ED0035895"
  },
  "name": "ogn123456",
  "description": "TEST_device",
  "attributes": {
  },
  "network_server_address": "eu1.cloud.thethings.network",
  "application_server_address": "eu1.cloud.thethings.network",
  "join_server_address": "eu1.cloud.thethings.network",
  "lorawan_version": "MAC_V1_0_3",
  "lorawan_phy_version": "PHY_V1_0_3_REV_A",
  "frequency_plan_id": "EU_863_870",
  "supports_join": True,
  "field_mask":{
      "paths":[
         "multicast",
         "supports_join",
         "lorawan_version",
         "ids.device_id",
         "ids.dev_eui",
         "ids.join_eui",
         "mac_settings.supports_32_bit_f_cnt",
         "supports_class_c",
         "supports_class_b",
         "lorawan_phy_version",
         "frequency_plan_id"
      ]
   }
}
###############################################################################################

res=getapidata(url, auth)
print (json.dumps(res, indent=4))
print ("len:", len(res["end_devices"]))

######################
#params = {'after': StartUtc,'Accept': 'text/event-stream'}
params = {'Accept': 'text/event-stream'}
headers = {
	'Authorization': auth
}
#API = (requests.get(('https://eu1.cloud.thethings.network/api/v3/as/applications/'+TTN_appid+'/packages/storage/uplink_message'),headers=headers,params=params)).text
#print ("API:", API)
###################

clicmd = "ttn-lw-cli end-devices delete ogn "+TTN_dev_id+" -c .ttn-lw-cli.yml "
print (clicmd)
os.system(clicmd)
clicmd = "ttn-lw-cli end-devices create ogn "+TTN_dev_id+" --name "+TTN_dev_id+" --description TEST_device -c .ttn-lw-cli.yml --dev-eui "+TTN_devEui+" --join-eui "+TTN_appEui+" --frequency-plan-id EU_863_870 --lorawan-version 1.0.3 --lorawan-phy-version 1.0.3-a" 
print (clicmd)
os.system(clicmd)
# "/api/v3/applications/ogn/devices/"+TTN_dev_id
API = (requests.get(('https://eu1.cloud.thethings.network/api/v3/applications/'+TTN_app_id+'/devices/'+TTN_dev_id),headers=headers,params=params)).text
print ("API GET:", API)
API = (requests.put(('https://eu1.cloud.thethings.network/api/v3/applications/'+TTN_app_id+'/devices/'+TTN_dev_id),headers=headers,params=params)).text
print ("API DEL:", API)
# api/v3/applications/{end_device.ids.application_ids.application_id}/devices
url = 'https://eu1.cloud.thethings.network/api/v3/applications/'+TTN_app_id+'/devices/'
params_json = json.dumps(adddevice)
#API = (requests.post((url),headers=headers,params=params, data=params_json)).text
API = requests.post(url, headers=headers, data=params_json)
print ("API POST:", API.text, url, params_json)
ids = {
    "device_id": "ogn123456",
    "application_ids": {"application_id" : "ogn"},
    "dev_eui": "0000CC50E3123456",
    "join_eui": "70B3D57ED0035895",
    "dev_addr": "27112303"
}

params = {"ids":ids,
          "name": "ogn123456",
          "description": "TEST_device"
          }

params_json = json.dumps(params)
data1 = requests.post(url, headers=headers, data=params_json)
print (data1.text)

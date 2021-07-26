#!/usr/bin/python3
######################################################################
# This program reads the config params inside the tracker and set the new ones
######################################################################
import ttn
import json
import datetime
import os
import binascii
import base64
import requests
import netparams as net


def signal_term_handler(signal, frame):
    mqtt_client.close()
    print('got SIGTERM ... Bye...: ', counter)
    os._exit(0)

########
def getdevappkey(app_client, dev_id):		# get the TTN app key from device id
    device      = app_client.device(dev_id)	# instantiate the device
    ld= device.lorawan_device			# get the device
    APP_key  = binascii.b2a_hex(ld.app_key).decode('utf-8').upper() # convert to HEX
    return (APP_key)

print ("TheThingsNetwork (TTN) network activity...")

net.TTN_dev_id      = "ognc3088c"
net.TTN_dev_Eui     = "00002462ABC3088C"
regist="IGC"
compid="XX"
devicedict = {      	# the device dict
        "description"     : "OGN/IGC-"+regist+" ",
        "appEui"          : net.TTN_appEui,
        "devEui"          : net.TTN_devEui, 
        "appKey"          : binascii.b2a_hex(os.urandom(16)).upper(), 
        "fCntUp"          : 10,
        "fCntDown"        : 11,
        "latitude"        : 39,
        "longitude"       : -3,
        "altitude"        : 600,
        "disableFCntCheck": True,
        "uses32BitFCnt"   : True,
        "attributes"      : { "info": compid},
      }
# ------------------------------------------------------------------ #
handler     = ttn.HandlerClient    (net.TTN_app_id, net.TTN_appKey)
app_client  = ttn.ApplicationClient(net.TTN_app_id, net.TTN_appKey, handler_address="", cert_content="/home/angel/.ssh/id_ras.pub", discovery_address="discovery.thethings.network:1900")
try:
   device      = app_client.device(net.TTN_dev_id)
   ld          = device.lorawan_device
   APP_eui     = binascii.b2a_hex(ld.app_eui).decode('utf-8').upper()
   DEV_eui     = binascii.b2a_hex(ld.dev_eui).decode('utf-8').upper()
   DEV_addr    = binascii.b2a_hex(ld.dev_addr).decode('utf-8').upper()
   APP_key     = binascii.b2a_hex(ld.app_key).decode('utf-8').upper()
   lastseen    = int(ld.last_seen/1000000000)
   tme         = datetime.datetime.utcfromtimestamp(lastseen)
   print ("Device:   ", ld.dev_id, "On application:", ld.app_id, " with APPeui:", APP_eui, "DEVeui:", DEV_eui, "DEVaddr:", DEV_addr, "APPkey:", APP_key, "Last Seen:", tme.strftime("%y-%m-%d %H:%M:%S"))    
   print ("DevAppKey:", getdevappkey(app_client, net.TTN_dev_id), "\n")
except:
   print ("error")

###################################################################################################################################################################

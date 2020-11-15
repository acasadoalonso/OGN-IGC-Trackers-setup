#!/usr/bin/python3
# ---------------------------------------------------------------------------- #
# This program test the TTN API and monitor the activity of the OGN application
# ---------------------------------------------------------------------------- #
import time
import ttn
import ogndecode
import json
import datetime
import signal
import os
import binascii
import base64
from python_cayennelpp.decoder import decode

#
# Channels on RAK7204 tracker
#
# Channel 1 GPS (Alt, lat, Lon)
#         2 Temperature
#         3 Accelerometer (XYZ)
#         4 
#         5 Gyro (XYZ)
#         6 Barometer
#         7 
#         8 Bat. voltage
#         9 magnetometer X
#        10 magnetometer Y
#        11 magnetometer Z
# =============================
#  struct
#   { unsigned int Address    :24; // aircraft address
#     unsigned int AddrType   : 2; // address type: 0 = random, 1 = ICAO, 2 = FLARM, 3 = OGN
#     unsigned int NonPos     : 1; // 0 = position packet, 1 = other information like status
#     unsigned int Parity     : 1; // parity takes into account bits 0..27 thus only the 28 lowest bits
#     unsigned int Relay      : 2; // 0 = direct packet, 1 = relayed once, 2 = relayed twice, ...
#     unsigned int Encrypted  : 1; // packet is encrypted
#     unsigned int Emergency  : 1; // aircraft in emergency (not used for now)
#   } Header ;

def signal_term_handler(signal, frame):
    mqtt_client.close()
    print('got SIGTERM ... Bye...: ', counter)
    os._exit(0)


def uplink_callback(msg, client):			# process the received message
  date = datetime.datetime.utcnow()                	# get the date
  tme = date.strftime("%y-%m-%d %H:%M:%S")           	# today's date
  global counter

  TTN={}						# TTN data
  Magn={}						# magnetometer data
  #print(msg)						# tuple with the message
  port=msg.port						# port
  pl=msg.payload_raw					# payload
  pf=msg.payload_fields					# payload fields
  appid=msg.app_id					# application ID
  devid=msg.dev_id					# device id
  HWser=msg.hardware_serial				# hardware serial
  cnter=msg.counter					# TTN counter
  #print ("Payload:", pl, len(pl), "\n\n")
  print("\nReceived uplink from ", msg.dev_id, " UTC time: ", tme, "Fields:", pf, "Port=", port, "Pll", len(pl))
  if len(pl)==28 or len(pl) == 24 and port == 1:	# if coming for an OGN tracker
     if len(pl) == 24:					# add the implicit header
        base64_bytes  = pl.encode('utf-8')		# converted to bytes
        message_bytes = base64.b64decode(base64_bytes)	# convert to ascii
        pl=base64.b64encode(b'\x00\x00\x00\x03'+message_bytes).decode('utf-8')	# add the implicit header
        #print ("PLL", len(pl))  
     if len(pl) == 28:					# check the header
        base64_bytes  = pl.encode('utf-8')		# converted to bytes
        message_bytes = base64.b64decode(base64_bytes)	# convert to ascii
        messageb = binascii.hexlify(message_bytes)	# convert to ascii hex
        print ("Hdr:", messageb)
        if message_bytes[3] == 0x07:
           print ("Encrypted:", messageb[0:6], DK)	# decode the encrypted message
           j=ogndecode.ogn_decode_func(pl, DK[0], DK[1], DK[2], DK[3])
        else:
           j=ogndecode.ogn_decode_func_plain(pl)	# decode the OGN/IGC tracker payload
     #print("J:tring===>>>",j,"\n\n")
     try:
        m = json.loads(j)
        #print ("\n>>>OGN Msg:",m, "\n")
        TTNmsg=m
        if m['Addr'] == '0x0     ':
           addr=getdeveui(devid)[10:]
           #print ("Addr:", addr)
           m['Addr'] = '0x'+addr.upper()
           
     except Exception as e:
        print (e, "J string: ===>", j, "<<<=\n\n")
        return
  if port == 1 and len(pl) != 28:			# check for errors
     print (">>> warning, payload lenght !!!", len(pl), pl, msg)
     return
  if port == 8:						# if coming form an TTN tracker
     base64_bytes = pl.encode('utf-8')			# convert to bytes
     message_bytes = base64.b64decode(base64_bytes)	# decode the base64 message
     messageb = binascii.b2a_hex(message_bytes)		# convert to ascii hex
     message = messageb.decode('ascii')			# convert bytes to ascii
     #print("msg:", message)
     LPPdecode=decode(message)				# decode the TTN LPP payload
     #print("\n>>LPP Msg:", LPPdecode,"\n\n")
     for ch in LPPdecode:				# check the channels
          #print (ch, ch['channel'])
          if ch['channel'] == 1:			# GPS channel
             TTN['Lat']=ch['value']['lat']
             TTN['Lon']=ch['value']['long']
             TTN['Alt']=ch['value']['alt']
          elif ch['channel'] == 2:			# temp channel
             TTN['Temp']=ch['value']
          elif ch['channel'] == 3:			# accelerometer channel
             TTN['Accel']=ch['value']
          elif ch['channel'] == 5:			# gyro channel
             TTN['Gyro']=ch['value']
          elif ch['channel'] == 6:			# baro channel
             TTN['Baro']=ch['value']
          elif ch['channel'] == 8:			# Battery voltage channel
             TTN['BVolt']=ch['value']
          elif ch['channel'] == 9:			# build the magnetomer channel
             Magn['x']=ch['value']
          elif ch['channel'] == 10:
             Magn['y']=ch['value']
          elif ch['channel'] == 11:
             Magn['z']=ch['value']
             TTN['Magn']=Magn
          else:
             print(">>>ch", ch)				# report the error
     #print(">>>TTN", TTN)
     TTNmsg=TTN
  print("Device:",getdeveui(devid),">>>:", TTNmsg, "<<<:", counter,"\n\n")
  counter += 1
  return

def connect_callback(res, client):
  date = datetime.datetime.utcnow()                	# get the date
  tme = date.strftime("%y-%m-%d %H:%M:%S")           	# today's date
  if res:
     print("TTN connected: ", tme,"\n\n")
  return

def getdevappkey(app_client):
    device      = app_client.device(dev_id)
    ld= device.lorawan_device
    APP_key  = binascii.b2a_hex(ld.app_key).decode('utf-8').upper()

    return(APP_key)
def getdeveui(dev_id):

    app_id      = "ogn"
    appEui      = "70B3D57ED0035895"
    appKey      = "ttn-account-v2.V4Z-WSzqhfR0FKiKFYu4VLgNEbxP9QluACwD1pSfwmE"
    handler     = ttn.HandlerClient    (app_id, appKey)
    app_client  = ttn.ApplicationClient(app_id, appKey, handler_address="", cert_content="/home/angel/.ssh/id_ras.pub", discovery_address="discovery.thethings.network:1900")
    device      = app_client.device(dev_id)
    ld	        = device.lorawan_device
    DEV_eui     = binascii.b2a_hex(ld.dev_eui).decode('utf-8').upper()
    return(DEV_eui)
# .....................................................................#
signal.signal(signal.SIGTERM, signal_term_handler)
# .....................................................................#


app_id     = "ogn"
dev_id     = "ogn60e6a0"
dev_id     = "ogn8e20f0"
dev_id     = "ognrakac"
appEui     = "70B3D57ED0035895"
appKey     = "ttn-account-v2.V4Z-WSzqhfR0FKiKFYu4VLgNEbxP9QluACwD1pSfwmE"
devAddr = "26013001"
nwkSKey = "7B4B28D2A6986E6B7B0F850FD82D2C8E"
appSKey = "D41213F2FD70952D22EE0FBE486E7490"
encr = True
counter = 0
DK=[]
keyfilename='keyfile'		# name of the file containing the encryption keys


devicetest = {
  		"description": "OGN-Tracker-test1",
  		"appEui": "70B3D57ED0035895",
  		"devEui": "00003C71BF60E6A0",
  		"appKey": binascii.b2a_hex(os.urandom(16)).upper(), # remove for ABP
  		"fCntUp": 10,
  		"fCntDown": 11,
  		"latitude": 100,
  		"longitude": 200,
  		"altitude": 300,
  		"attributes": {
      			"OGNIGC": "True",
  		},
  		"disableFCntCheck": True,
  		"uses32BitFCnt": True,
}
my_device = {
            	"appEui": "70B3D57ED0035895",
            	"devEui": "00003C71BF60E6A0",
            	"appKey": appKey,
            	"devAddr": "26014FDF", # remove for OTAA
            	"nwkSKey": binascii.b2a_hex(os.urandom(16)).upper(), # remove for OTAA
            	"appSKey": binascii.b2a_hex(os.urandom(16)).upper(), # remove for OTAA
            	"disableFCntCheck": True,
            	"uses32BitFCnt": True,
        }

#
########################################################################
#
handler     = ttn.HandlerClient    (app_id, appKey)
app_client  = ttn.ApplicationClient(app_id, appKey, handler_address="", cert_content="/home/angel/.ssh/id_ras.pub", discovery_address="discovery.thethings.network:1900")
device      = app_client.device(dev_id)
ld	    = device.lorawan_device
APP_eui     = binascii.b2a_hex(ld.app_eui).decode('utf-8').upper()
DEV_eui     = binascii.b2a_hex(ld.dev_eui).decode('utf-8').upper()
DEV_addr    = binascii.b2a_hex(ld.dev_addr).decode('utf-8').upper()
APP_key     = binascii.b2a_hex(ld.app_key).decode('utf-8').upper()
lastseen    = int(ld.last_seen/1000000000)
tme         = datetime.datetime.utcfromtimestamp(lastseen)

if encr:
   from Keys import *
   key=getkeyfile(keyfilename)	# get the key from the keyfile
   DecKey=getkeys(DK, key)	# get the keys 4 words
   print ("Keys:",DK)

#print (ld.dev_id, ld.app_id, "APPeui:", APP_eui, "DEVeui:", DEV_eui, "DEVaddr:", DEV_addr, "Last Seen:", tme.strftime("%y-%m-%d %H:%M:%S"))    

#print ("DevAppKey:", getdevappkey(app_client))
#devices     = app_client.devices()
#for dd in devices:
    #print ("DDD:", dd)
#app         = app_client.get()
#print ("AAA:", app)
# --------------------------------------------------------- #
#
# using mqtt client
#
# --------------------------------------------------------- #

mqtt_client = handler.data()
mqtt_client.set_uplink_callback(uplink_callback)
mqtt_client.set_connect_callback(connect_callback)
mqtt_client.connect()
while True:
      try:
         time.sleep(60)
         pass
      except SystemExit:
         print (">>>>: System Exit <<<<<<\n\n")
         mqtt_client.close()
         break
      except KeyboardInterrupt:
         print (">>>>: Keyboard Interupt <<<<<<\n\n")
         mqtt_client.close()
         break
         
print ("Bye: ...: ", counter)
exit(0)

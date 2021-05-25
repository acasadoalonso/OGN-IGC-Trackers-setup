#!/usr/bin/python3
######################################################################
# This program reads the config params inside the tracker and set the new ones
######################################################################
import argparse
import serial
from time import sleep          # use the sleep function
import time
import ttn
import json
import datetime
import signal
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

########
def getHEL_DEVID(dev_eui):				# return the Helium ID based on the lorawan EUI
    r = requests.get(net.HEL_URL, headers=net.HEL_header)         	# get the list of devices
    devices=r.json()					# read the data
    for dev in devices:
        if dev['dev_eui'] == dev_eui:			# it is our dev-eui ??
           return (dev['id'])				# return tghe Helium ID
    return 0

########
def printparams(ser, trkcfg, prt=False):	# print the parameters 
				# ser serial, trkcfg the tracker configuration table possible values
    ID=""			# tracker ID
    MAC=""			# tracker MAC ID
    cnt=0
    param={}			# params decoded
    etx=b'\x03'			# the Control C
    while cnt < 100:		# at least 100 lines !!!
        line = ser.readline()   # read a '\n' terminated line
        if len(line) == 0:      # end of data ???
           break		# all done
        l=line.decode('utf-8').rstrip()
        if line	[0:3] == 'I (':
           continue
        if cnt == 0:		# first line is the ID
           ID=line[0:10]
           if ID[0:4] != b'1:3:':
              print("ID>>>:", ID)
              ser.write(etx)	# send a Ctrl-C 
              continue
           if line[10:11] == b'/':
              MAC=line[11:23]
        if l[0:7] == '/spiffs':	# ignore the spiffs lines
           continue
        if prt:
        	print (l)	# print the data received
        cnt += 1		# increase the counter
        sv=l.find(" = ")	# look for the = sign
        if sv == -1:		# if not found ignore the line
           continue
        for par in trkcfg:	# scan for config parameters
            s  = l.find(' ')	# look for te first space
            p  = l[0:s]		# get only the first token
            sc = l.find(';')	# look for the end of the value
            v  = l[sv+3:sc]	# get the value
            if par == p :	# it is our param ?
               if v[0:2] == '0x':
                  v=int(v, 16)
               param[par]=v	# yes, save the value 
               break
    if ID == '':
       print ("ID:", ID, "Please check if the tracker is ON !!!") 
       return False  
    trackerID=ID[4:].decode('utf-8')
    MAC=MAC.decode('utf-8')
    param["TrackerID"]=trackerID
    param["MAC"]=MAC
    if prt:
    	print ("Tracker ID:", trackerID, "MAC:", MAC)
    	print ("Parameters:\n", param, "\n")
    return(param)		# return the table with the parameters already parsed
#######
trkcfg=[ "Address", 		# config parameters to scan
         "AddrType",
         "AcftType",
         "Encrypt",
         "EncryptKey[0]",
         "EncryptKey[1]",
         "EncryptKey[2]",
         "EncryptKey[3]",
         "PublicKey",
         "Verbose",
         "BTname",
         "Pilot",
         "Crew",
         "Manuf",
         "Model",
         "Type",
         "SN",
         "ID",
         "Reg",
         "Class",
         "Task",
         "Base",
         "ICE",
         "TrackerID",
         "PilotID"]

#######
REG_URL = "http://acasado.es:60080/registration/V1/?action=REGISTER&token="      # the OGN registration source
#REG_URL = "http://localhost:8181/?action=REGISTER&token="                       # the OGN registration source

def setregdata(mac, reg, devid, uniqueid, publickey, prt=True):         # set the data from the API server
    date = datetime.datetime.utcnow()       # get the date
    dte = date.strftime("%Y-%m-%d")         # today's date
    nonce = base64.b64encode(dte.encode('utf-8')).decode('ascii')
    url=REG_URL+nonce
    if reg == '':
       url=url+'&registration=NONE'
    else:
       url=url+'&registration='+reg
    url=url+'&mac='+mac+'&devid='+devid+'&uniqueid='+uniqueid+'&publickey='+publickey
    if prt:
       print(url)
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")  # it return a JSON string
    req.add_header("Content-Type", "application/hal+json")
    r = urllib.request.urlopen(req)         # open the url resource
    js=r.read().decode('UTF-8')
    j_obj = json.loads(js)                  # convert to JSON
    return j_obj 


# .....................................................................#
signal.signal(signal.SIGTERM, signal_term_handler)
# .....................................................................#


#######
# --------------------------------------#
#
# OGN tracker SETUP manager 
#
# --------------------------------------#
#######
print ("\n\nOGN tracker setup program:\n==========================\nIt gets the information from the tracker firmware and handles the setup parameter.\nThe tracker must be connected to the USB port.")
print ("Args: -p print ON|OFF, -u USB port, -s setup on|off, -k print the keys on|off, -kf keyfile name, -o Use the OGNDDB, -t register on the TTN network, -n encrypt on|off, -r register on the registration DB")
print ("============================================================================================================================================\n\n")
parser = argparse.ArgumentParser(description="Manage the OGN TRACKERS setup parameters")
parser.add_argument('-p', '--print',       required=False, dest='prt',      action='store', default=False)
parser.add_argument('-u', '--usb',         required=False, dest='usb',      action='store', default=0)
parser.add_argument('-s', '--setup',       required=False, dest='setup',    action='store', default=False)
parser.add_argument('-k', '--printkeys',   required=False, dest='keys',     action='store', default=False)
parser.add_argument('-kf','--keyfile',     required=False, dest='keyfile',  action='store', default='keyfile')
parser.add_argument('-o', '--ognddb',      required=False, dest='ognddb',   action='store', default=True)
parser.add_argument('-t', '--ttn',         required=False, dest='ttn',      action='store', default=False)
parser.add_argument('-m', '--helium',      required=False, dest='helium',   action='store', default=False)
parser.add_argument('-n', '--encrypt',     required=False, dest='encr',     action='store', default=False)
parser.add_argument('-r', '--register',    required=False, dest='reg',      action='store', default=False)

args  	= parser.parse_args()
prt   	= args.prt		# print debugging
setup 	= args.setup		# setup the tracker
keys  	= args.keys		# print encryption keys
usb   	= args.usb		# USB port where the tracker is connected	
keyfile	= args.keyfile		# file containing the encryption keys	
ognddb	= args.ognddb		# use the OGN DDB for registration data
ttnopt	= args.ttn		# Register on the TheThingsNetwork (TTN)
helopt	= args.helium		# Register on the Helium Network
regopt	= args.reg		# register the device
encr	= args.encr		# Set encryption mode

if ognddb == "False":		# use the OGN DDB to get the data
   ognddb = False
else:
   ognddb = True			

if ttnopt == "True":		# register at the TTN network
   ttnopt = True
else:
   ttnopt = False			

if helopt == "True":		# register at the helium network
   helopt = True
else:
   helopt = False			

if regopt == "True":		# register the device
   regopt = True
   ognddb = True		# register froce to use the OGN DDB			
else:
   regopt = False			

if encr == "True":		# set encryption mode
   encr = True
else:
   encr = False			

if ttnopt and helopt:
   print("ERROR: Both networks TTN & Helium can not be chosen at the same time !!!\n\n")

# --------------------------------------#
keyfilename=keyfile		# name of the file containing the encryption keys
keyfilename='keyfile'		# name of the file containing the encryption keys
etx=b'\x03'			# the Control C
if encr:
   from Keys import *
   DecKey=[]			# the 4 hex values of the key
   key=getkeyfile(keyfilename)	# get the key from the keyfile
   DecKey=getkeys(DecKey, key)	# get the keys 4 words
   print ("Keys:",DecKey)
# --------------------------------------#

if not ognddb:			# deprecated code, it will be susbtituted by OGNDDB
   import config		# get the configuration parameters
   import MySQLdb               # the SQL data base routines
				# open the DataBase
   DBpath      = config.DBpath
   DBhost      = config.DBhost
   DBuser      = config.DBuser
   DBpasswd    = config.DBpasswd
   DBname      = config.DBname
   conn = MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)
   print("MySQL: Database:", DBname, " at Host:", DBhost)
else:
   from ognddbfuncs import *
   print("Using OGN DDB database \n")

# --------------------------------------#
if usb == '-1':
        exit(0)
				# set the parameters 
i=0
if encr:			# if use encryption
				# just prepare the encryption comd
    from Keys import *		# get the key handling functions
    import ogndecode
    encryptcmd=b'$POGNS,EncryptKey='# prepare the encryption keys
    for k in DecKey:		# prepare the format
        kh=hex(k)
        h=kh[2:]
        if i != 0:
          encryptcmd += b':'
        encryptcmd += h.encode('utf-8')
        if i == 3:
          encryptcmd += b'\n'
        if keys:
    	    print ("Key"+str(i)+":",h)
        i += 1
# -------------------------------------#
ser 			= serial.Serial()
ser.port 		= '/dev/ttyUSB'+str(usb)
ser.baudrate 		= 115200
ser.parity		= serial.PARITY_NONE
ser.timeout		= 1
ser.break_condition	= True

ser.open()			# open the tracker console
#--------------------------------------#

ser.send_break(duration=0.25)	# send a break 
ser.write(b'$POGNS,Verbose=0\n')# make no verbose to avoid other messages
ser.write(b'$POGNS,Verbose=0\n')# do it again
ser.write(etx)			# send a Ctrl-C 
sleep(1)			# wait a second to give a chance to receive the data
#--------------------------------------#

try:
   param=printparams(ser, trkcfg, prt)# get the configuration parameters
except:
   ser.write(b'$POGNS,BTname=123456\n')# make no verbose to avoid other messages
   ser.write(b'$POGNS,BTname=123456\n')# do it again
   ser.write(etx)		# send a Ctrl-C 
   param=printparams(ser, trkcfg, prt)# get the configuration parameters
if param == False:		# if noot found, nothing else to do
   exit(1)
#--------------------------------------#

ID=param['TrackerID']		# get the tracker ID
MAC=param['MAC']		# get the tracker MAC ID
#publickey=param['PublicKey']	# get the Public Key from the tracker ==> reg DB
publickey="1234567890ABCDEF1234567890ABCDEF"    # <<<<<<< TEST
if not prt:
   print (param)		# if not prints it yet 
   print("\n\nTracker ID=", ID, "MAC", MAC, "\n\n")# tracker ID
if keys and encr:
	print (encryptcmd) 	# print the encrypt command
if setup and encr:
	ser.write(encryptcmd)	# Write the encryption keys
	ser.write("$POGNS,Encrypt=1".encode('utf-8')) 
	print("$POGNS,Encrypt=1".encode('utf-8')) 
sleep(1)			# wait a second to give a chance to receive the data
#--------------------------------------#

found=False			# assume not found YET

if ognddb:			# if using the OGN DDB
   devid=ID
   info=getogninfo(devid)	# get the info from the OGN DDB
   if 'return' in info or info == "NOInfo":
        print("Device "+devid+" not registered on the OGN DDB\n", info)
        pass			# nothing to do
   else:
        if prt:
           print ("INFO: :::", info)
        ogntid 	= info['device_id']	# OGN tracker ID
        if 'device_aprsid' in info:
            flarmid = info['device_aprsid']	# Flarmid id to be linked
        else:
            flarmid = ogntid
        devtype = info['device_type']	# device type (glider, powerplane, paraglider, etc, ...)
        regist 	= info['registration'] 	# registration id to be linked
        pilot 	= 'OGN/IGC_Tracker'  	# owner
        compid 	= info['cn']  		# competition ID
        model  	= info['aircraft_model']  	# model
        uniqueid= info['uniqueid']	# unique id
        print ("From OGN DDB:", ogntid, devtype, flarmid, regist, pilot, compid, model, uniqueid) 
        found=True
else:				# deprecated code

   curs = conn.cursor()         # set the cursor for searching the devices
                                # get all the devices with OGN tracker
   curs.execute("select id, flarmid, registration, owner, compid, model from TRKDEVICES where devicetype = 'OGNT' and active = 1 and id = '"+ID+"'; ")
   for rowg in curs.fetchall():	# look for that registration on the OGN database

        ogntid 	= rowg[0]	# OGN tracker ID
        flarmid = rowg[1]	# Flarmid id to be linked
        regist 	= rowg[2]  	# registration id to be linked
        pilot 	= rowg[3]  	# owner
        compid 	= rowg[4]  	# competition ID
        model  	= rowg[5]  	# model
        devtype = 1		# always glider
        info    = {'device_id': ogntid, 'device_aprsid':flarmid, 'device_type' : 1, 'registration': regist, 'pilot' : pilot, 'cn': compid, 'aircraft_model' : model}
        print ("From DB:", ogntid, flarmid, regist, pilot, compid, model) # whatch out for multiples Ids !!!!
        print (info)
        if found:		# if found one already ???
           print("WARNING: Multiple IDs for the same tracker !!!! --> ", ID, ogntid)
        found=True
   if not found:
        print ("Device "+ID+" not found on the REG DataBase\n\n")

print( "==============================================================================================\n\n")

if found:			# set the last one !!!
   APP_key=''			# for the $POGNS cmd
   if ttnopt and not helopt:			# if TTN registration
      print ("TheThingsNetwork (TTN) network activity...")

      devicetest = {      	# the device dict
        "description"     : "OGN/IGC-"+regist+" ",
        "appEui"          : net.TTN_appEui,
        "devEui"          : "0000"+MAC,
        "appKey"          : binascii.b2a_hex(os.urandom(16)).upper(), 
        "fCntUp"          : 10,
        "fCntDown"        : 11,
        "latitude"        : 100,
        "longitude"       : 200,
        "altitude"        : 300,
        "disableFCntCheck": True,
        "uses32BitFCnt"   : True,
        "attributes"      : { "info": compid},
      }
      # ------------------------------------------------------------------ #
      net.TTN_dev_id      = flarmid.lower()
      handler     = ttn.HandlerClient    (net.TTN_app_id, net.TTN_appKey)
      app_client  = ttn.ApplicationClient(net.TTN_app_id, net.TTN_appKey, handler_address="", cert_content="/home/angel/.ssh/id_ras.pub", discovery_address="discovery.thethings.network:1900")
      if setup:
         try:
            app_client.delete_device  (net.TTN_dev_id)
         except:
            print ("Deleting Device:", net.TTN_dev_id, "with MAC:", MAC, "Not registered on the TTN\n")
         try:   
            app_client.register_device(net.TTN_dev_id, devicetest)
         except Exception as e:
            print ("Registering  Device error:", net.TTN_dev_id, "with MAC:", MAC,"Error:", e, "\n")
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

         #cmd="$POGNS,AppKey="+APP_key+"\n"
         #print(cmd)
      except Exception as e:
         print ("Device:", net.TTN_dev_id, "with MAC:", MAC, "Not registered on the TTN Error: ", e, "\n")

   # end of if ttnopt
   
   if helopt and not ttnopt:			# if Helium registration
      print ("Helium network activity...")
      net.HEL_dev_id       = flarmid.lower()
      net.HEL_dev_eui      = "0000"+MAC
      net.HEL_name         = "OGN/IGC Tracker "+net.HEL_dev_id+" "+regist 
      net.HEL_DEVID        = getHEL_DEVID(net.HEL_dev_eui)			# get the Hellium ID for the list of devices
      if net.HEL_DEVID != 0:	# just report that exists
         print ("Helium DEVID:", net.HEL_DEVID, "exists for eui:", net.HEL_dev_eui, "deleting it now ...")
         url=net.HEL_URL+'/'+net.HEL_DEVID
         r = requests.delete(url, headers=net.HEL_header)         		# open the url resource
         if r.status_code != 200:
            print("ERROR: Device NOT deleted: ", r.status_code, '!!!\n')
      payload = {"name":    net.HEL_name, 					# prepare the POST request
                 "app_eui": net.HEL_app_eui, 
                 "app_key": net.HEL_app_key, 
                 "dev_eui": net.HEL_dev_eui}
      r = requests.post(net.HEL_URL, headers=net.HEL_header, data=payload)      # open the url resource
      if r.status_code != 200 and r.status_code != 422 and r.status_code != 201:
         print("ERROR: Creating device RC:", r.status_code, '!!!\n\n')
      net.HEL_DEVID        = getHEL_DEVID(net.HEL_dev_eui)
      if net.HEL_DEVID == 0:
         print("ERROR: device not created !!!\n")
      print ("Helium DEVID:", net.HEL_DEVID, "created for eui:", net.HEL_dev_eui)
      r = requests.post(net.HEL_URL+'/'+net.HEL_DEVID+'/labels', headers=net.HEL_header, data=net.HEL_label)         # open the url resource
      if r.status_code != 200:
         print("ERROR: Add label to device:", r.status_code, '!!!\n')
      url=net.HEL_URL+'/'+net.HEL_DEVID
      #print (url, '\n\n')
      r = requests.get(url, headers=net.HEL_header)         		# open the url resource
      if r.status_code != 200:
         print("ERROR: Device data RC: ", r.status_code, '!!!\n')
      print("Device data :", json.dumps(r.json(), indent=4))
      print("Device:   ", net.HEL_DEVID,  " with APPeui:", net.HEL_app_eui, "DEVeui:", net.HEL_dev_eui, "DEVaddr:", net.HEL_dev_eui, "APPkey:", net.HEL_app_key, "Name: ", net.HEL_name, "\n\n")    
      APP_key=net.HEL_app_key						# for the $POGNS
   # end of if helopt

# ------------------------------------------------------------------ #

   if setup:			# if setup is required 
        cmd="$POGNS,Reg="+regist+"\n"
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,Pilot="+pilot+"\n"
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,ID="+compid+"\n"
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,Model="+model+"\n"
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,SN="+flarmid+"\n"
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,BTname="+flarmid+"\n"
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,Type="+str(devtype)+"\n"
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,AppKey="+APP_key+"\n"
        ser.write(cmd.encode('UTF-8'))
        ser.write(etx)		# send a Ctrl-C 
        sleep(1)		# wait a second to give a chance to receive the data
        printparams(ser, trkcfg, False)# print the new parameters

   if regopt:			# if registration on the registration DB
        print("PPP", MAC, regist, ID, uniqueid, publickey)
        r=setregdata(MAC, regist, ID, uniqueid, publickey)
        print ("Registration at server: ", r)

else:
   print("No information about the device "+ID+" on the databases !!!\n\n")
print( "==============================================================================================")
ser.close()
###################################################################################################################################################################

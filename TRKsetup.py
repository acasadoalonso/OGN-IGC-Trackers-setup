#!/usr/bin/python3
######################################################################
# This program reads the config params inside the tracker and set the new ones
######################################################################
import argparse
import serial
from   time import sleep          # use the sleep function
import time
import ttn
import json
import datetime
import signal
import os
import binascii
import base64
import requests
import urllib.parse
import netparams as net
from os import path

########
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
def getHEL_DEVID(dev_eui):			# return the Helium ID based on the lorawan EUI
    r = requests.get(net.HEL_URL, headers=net.HEL_header)         	# get the list of devices
    devices=r.json()				# read the data
    for dev in devices:
        if dev['dev_eui'] == dev_eui:		# it is our dev-eui ??
           return (dev['id'])			# return tghe Helium ID
    return 0

########
def gettrkpublickey(ser, prt=False):		# Get the public key from the tracker
    publickey=""				# public key from tracker
    cnt=0
    eol=False
    found=False
    while cnt < 16:
        line = ser.readline()   		# read a '\n' terminated line
        #print ("LLL:", cnt, line)
        if len(line) == 0:      		# end of data ???
           if eol:
              break				# all done
           else:
              eol=True
              continue
        if not found and line[0:4] != b'----':	# skip the the NON PK lines
           continue
        if line[0:10] == b'-----BEGIN':		# starts the PK ???
           found = True
        l=line.decode('utf-8')
        publickey += l
        if line[0:8] == b'-----END PUBLIC KEY-----':
           break				# ignore the after lines

    return publickey
########
def printparams(ser, trkcfg, prt=False):	# print the parameters 
					# ser serial, trkcfg the tracker configuration table possible values
    ID=""				# tracker ID
    MAC=""				# tracker MAC ID
    cnt=0
    eol=False
    param={}				# params decoded
    etx=b'\x03'				# the Control C
    while cnt < 256:			# at least 256 lines !!!
        line = ser.readline()   	# read a '\n' terminated line
        #print ("LLL:", cnt, line)
        if len(line) == 0:      	# end of data ???
           if eol:
              break			# all done
           else:
              eol=True
              continue
        l=line.decode('utf-8').rstrip()
        if line	[0:3] == 'I (':
           continue
        if cnt == 0:			# first line is the ID
           ID=line[0:10]
           if ID[0:4] != b'1:3:' and ID[0:4] != b'1:0:': 	# either normal or stealth
              print("ID>>>:", ID, "<<<")
              ser.write(etx)		# send a Ctrl-C 
              continue
           if line[10:11] == b'/':
              MAC=line[11:27]
        if l[0:7] == '/spiffs':		# ignore the spiffs lines
           continue
        if prt:
        	print (l)		# print the data received
        cnt += 1			# increase the counter
        sv=l.find(" = ")		# look for the = sign
        if sv == -1:			# if not found ignore the line
           continue
        for par in trkcfg:		# scan for config parameters
            s  = l.find(' ')		# look for te first space
            p  = l[0:s]			# get only the first token
            sc = l.find(';')		# look for the end of the value
            v  = l[sv+3:sc]		# get the value
            if par == p :		# it is our param ?
               if v[0:2] == '0x':
                  v=int(v, 16)
               param[par]=v		# yes, save the value 
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
    return(param)			# return the table with the parameters already parsed

#######
trkcfg=[ "Address", 			# config parameters to scan
         "AddrType",
         "AcftType",
         "Stealth",
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
         "Hard",
         "Soft",
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
REG_URL = "http://glidertracking.fai.org/registration/V1/?action=REGISTER&token="      # the OGN registration source
#REG_URL = "http://localhost:8181/?action=REGISTER&token="                       # the OGN registration source

########
def setregdata(mac, reg, devid, uniqueid, publickey, prt=False):  
       						# REGISTER the data from the API server
    date = datetime.datetime.utcnow()       	# get the date
    dte = date.strftime("%Y-%m-%d")         	# today's date
    nonce = base64.b64encode(dte.encode('utf-8')).decode('ascii')
    url=REG_URL+nonce
    if reg == '':
       url=url+'&registration=NONE'
    else:
       url=url+'&registration='+reg		# build the URL
    url=url+'&mac='+mac+'&devid='+devid+'&uniqueid='+uniqueid+'&publickey='+urllib.parse.quote(publickey)
    if prt:
       print(url)
    req = urllib.request.Request(url)		# the url instacne
    req.add_header("Accept", "application/json")  # it return a JSON string
    req.add_header("Content-Type", "application/hal+json")
    r = urllib.request.urlopen(req)         	# open the url resource
    js=r.read().decode('UTF-8')			# get the response OK | not OK
    j_obj = json.loads(js)                  	# convert to JSON
    return j_obj 


# .....................................................................#
signal.signal(signal.SIGTERM, signal_term_handler)
# .....................................................................#


#######
# ----------------------------------------------------------------------#
#									#
# OGN tracker SETUP manager 						#
#									#
# ----------------------------------------------------------------------#
#######
Hard='AVX-1.0'
Soft='OGN-1.0'

print ("\n\nOGN TRKsetup program:\nVersion: "+Soft+"\n==========================\nIt gets the information from the tracker firmware and handles the setup parameter.\nThe tracker must be connected to the USB port.")
print ("\n\nArgs: -p print ON|OFF, -u USB port, -s setup on|off, -kf keyfile name, -o Use the OGNDDB, -t register on the TTN network, -n encrypt on|off, -r register on the registration DB, --pairing FLARMID pairing with this Flarm, --owner for pairing")

#					  report the program version based on file date
print ("==========================================================================================================================================================================================\n\n")
if os.name != 'nt':			# just report the version, not valid on NT or bundles from pyinstaller
   bundle_dir = path.abspath(path.dirname(__file__))
   if bundle_dir[0:9] != "/tmp/_MEI":
      print("Program Version:", time.ctime(os.path.getmtime(path.abspath(__file__))))
      print("=========================================")
# -------------------------------------------------------------------------------------------------------- #
parser = argparse.ArgumentParser(description="Manage the OGN TRACKERS setup parameters")
parser.add_argument('-p', '--print',       required=False, dest='prttxt',   action='store', default='False',  help='Set print ON|OFF')
parser.add_argument('-u', '--usb',         required=False, dest='usb',      action='store', default='USB0',   help='The USB port where the tracker is connected')
parser.add_argument('-s', '--setup',       required=False, dest='setup',    action='store', default=False,    help='Do the setup on the tracker')
parser.add_argument('-kf','--keyfile',     required=False, dest='keyfile',  action='store', default='keyfile',help='Name of the file containing the keys, privided by the IGC')
parser.add_argument('-o', '--ognddb',      required=False, dest='ognddb',   action='store', default=True,     help='Use the OGN DDB for the setup')
parser.add_argument('-t', '--ttn',         required=False, dest='ttn',      action='store', default=False,    help='Setup for the TTN')
parser.add_argument('-m', '--helium',      required=False, dest='helium',   action='store', default=False,    help='Setup for Helium')
parser.add_argument('-n', '--encrypt',     required=False, dest='encr',     action='store', default=False,    help='Set the encryption ON|OFF')
parser.add_argument('-r', '--register',    required=False, dest='reg',      action='store', default=False,    help='Register this tracker on the FAI registration site')
parser.add_argument('-a', '--pairing',     required=False, dest='pairing',  action='store', default='False',  help='Pair this tracker with this Flarm')
parser.add_argument('-w', '--owner',       required=False, dest='owner',    action='store', default='False',  help='Name of the owner(optional)')
parser.add_argument('-st','--stealth',     required=False, dest='stealth',  action='store', default='False',  help='Stealth mode, non identified')

args  	= parser.parse_args()
prttxt 	= args.prttxt		# print debugging
setup 	= args.setup		# setup the tracker
usb   	= args.usb		# USB port where the tracker is connected	
keyfile	= args.keyfile		# file containing the encryption keys	
ognddb	= args.ognddb		# use the OGN DDB for registration data
ttnopt	= args.ttn		# Register on the TheThingsNetwork (TTN)
helopt	= args.helium		# Register on the Helium Network
regopt	= args.reg		# register the device
encr	= args.encr		# Set encryption mode
pairing	= args.pairing		# Set pairing ONGT & FLARM
owner	= args.owner		# Ownner of the FLARM to be paired
stealth	= args.stealth		# stealth mode - random ID and not identified

if prttxt == "True" or prttxt == 'TRUE' or prttxt == 'ON': # set print mode
   prt = True
else:
   prt = False			# may be changed by the config profile
if ognddb == "False":		# use the OGN DDB to get t5yyhe data
   ognddb = False
else:
   ognddb = True			

if ttnopt == "True" or ttnopt == "ON":		# register at the TTN network
   ttnopt = True
else:
   ttnopt = False			

if helopt == "True" or helopt == "ON":		# register at the helium network
   helopt = True
else:
   helopt = False			

if regopt == "True" or regopt == 'ON':		# register the device on the FAI server
   regopt = True
   ognddb = True		# register froce to use the OGN DDB			
else:
   regopt = False			

if encr == "True" or encr == 'ON':		# set encryption mode
   encr = True
else:
   encr = False			

if stealth == "True" or stealth == 'ON':	# set stealth mode
   stealth = True
else:
   stealth = False			

if ttnopt and helopt:
   print("ERROR: Both networks TTN & Helium can not be chosen at the same time !!!\n\n")

if pairing == "False":		# use the OGN DDB to get the data
   pairing = False
else:
   import config		# get the configuration parameters
   import MySQLdb               # the SQL data base routines
				# open the DataBase
   DBpath      = config.DBpath
   DBhost      = config.DBhost
   DBuser      = config.DBuser
   DBpasswd    = config.DBpasswd
   DBname      = config.DBname
   DBtable     ="TRKDEVICES"	# table for storing the pairing information
   ognddb      = True		# force true to use the OGN DDB
   conn = MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)
   print("Pairing on MySQL: Database:", DBname, " at Host:", DBhost)
   

if owner == "False":		# use the OGN DDB to get the data
   owner = False


etx=b'\x03'			# the Control C
VT=b'\x0B'			# the Control K

# -------------------------------------------------------------------------------#
				# deal with the encryption set the DecKey array
if encr:
   keyfilename=keyfile		# name of the file containing the encryption keys
   keyfileencrypted=keyfilename+'.encrypt'		# name of the file containing the keys encrypted
   print ("Encrypted file:", keyfileencrypted)		# 
   if not os.path.exists(keyfileencrypted):		# check if we have that file ???
      print ("The keyfile is NOT found !!! ...\n")
      os._exit(-1) 
   from Keysfuncs import *	# get the functions
   DecKey=[]			# the 4 hex values of the key
   privkey = getprivatekey('keypriv.PEM')		# get the private key to decrypt the file either from file or memory
   key=getkeyfromencryptedfile(keyfileencrypted, privkey) # decrypt the content of the file and get the encryption keys
   #print ("Key back from file:     ", key)
   #key=getkeyfile(keyfilename)	# get the key from the keyfile
   DecKey=getkeys(DecKey, key)	# get the keys 4 words
   #print ("Keys:",DecKey)

# -------------------------------------------------------------------------------#

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
if prttxt == "True" or prttxt == 'TRUE' or prttxt == 'ON': # set print mode
   prt = True			# the command takes precedence over the config profile

if usb == '-1':			# just a quick exit
        os._exit(0)

# -------------------------------------------------------------------------------------------- #

				# set the $POGNS commands 
i=0
if encr:			# if use encryption
				# just prepare the encryption comd
    encryptcmd=b'$POGNS,Encrypt=1,EncryptKey='# prepare the encryption keys
    for k in DecKey:		# prepare the format
        kh=hex(k)
        h=kh[2:]
        if i != 0:
          encryptcmd += b':'
        encryptcmd += h.encode('utf-8')
        if i == 3:
          encryptcmd += b'\n'
        i += 1
else:
    encryptcmd=b'$POGNS,Encrypt=0'# NO encryption


# -------------------------------------#
ser 			= serial.Serial()
ser.port 		= '/dev/tty'+usb
ser.baudrate 		= 115200
ser.parity		= serial.PARITY_NONE
ser.timeout		= 1
ser.break_condition	= True

try:
    ser.open()			# open the tracker console
except:
    print ("The TRACKER needs to be connected to the port: /dev/tty"+usb+" ...  \n")
    os._exit(-1)
#--------------------------------------#

ser.send_break(duration=0.25)	# send a break 
ser.write(b'$POGNS,Verbose=0\n')# make no verbose to avoid other messages
ser.write(b'$POGNS,Verbose=0\n')# do it again
ser.write(etx)			# send a Ctrl-C 
sleep(2)			# wait a second to give a chance to receive the data
#--------------------------------------#

try:				# receive the parameters
   param=printparams(ser, trkcfg, prt)
				# get the configuration parameters
except:				# just in case try again !!!
   ser.write(b'$POGNS,BTname=123456\n')# make 
   ser.write(b'$POGNS,BTname=123456\n')# do it again
   ser.write(etx)		# send a Ctrl-C 
   param=printparams(ser, trkcfg, prt)
				# get the configuration parameters
if param == False:		# if not found, nothing else to do
   print("Parameters from the trackers not found ... nothing else to do !!!!\n")
   os._exit(1)
#--------------------------------------#

ID	=param['TrackerID']	# get the tracker ID
MAC	=param['MAC']		# get the tracker MAC ID

if regopt:			# if we need to register the tracker 
   ser.write(VT)		# send a Ctrl-K 
   publickey=gettrkpublickey(ser) # get the public key

if param['Stealth'] == 1:
   stealthset=True
else:
   stealthset=False

if not prt:
   print("\n\nTracker ID=", ID, "MAC", MAC, "\n\n")# tracker ID

if setup and encr:
	ser.write(encryptcmd)	# Write the encryption keys
	ser.write("$POGNS,Encrypt=1".encode('utf-8')) 
	print("Encryption keys loaded !!!\n")
if setup and not encr:		# erase the encrypted mode
	ser.write("$POGNS,Encrypt=0".encode('utf-8')) 

sleep(2)			# wait a second to give a chance to receive the data

#--------------------------------------#

found=False			# assume not found YET

flarmid = MAC[-6:]
devtype = 1			# device type (glider, powerplane, paraglider, etc, ...)
regist 	= "NOREG" 		# registration id to be linked
pilot 	= 'OGN/IGC_Tracker'  	# owner
compid 	= "NO" 			# competition ID
model  	= "UNK"			# model
uniqueid= "0"			# unique ida

if ognddb and not stealthset:	# if using the OGN DDB
   devid=ID
   info=getogninfo(devid)	# get the info from the OGN DDB
   if 'return' in info or info == "NOInfo":
        print("Device "+devid+" not registered on the OGN DDB\n", info)
        pass			# nothing to do
   else:
        if prt:
           print ("INFO from OGN DDB==>: ", info, "<== ")
        ogntid 	= info['device_id']	# OGN tracker ID
        if 'device_aprsid' in info:
            flarmid = info['device_aprsid']	# Flarmid id to be linked
        else:
            flarmid = ogntid
        devtype = info['device_type']	# device type (glider, powerplane, paraglider, etc, ...)
        regist 	= info['registration'] 	# registration id to be linked
        pilot 	= 'OGN/IGC_Tracker'  	# owner
        compid 	= info['cn']  		# competition ID
        model  	= info['aircraft_model'] # model
        uniqueid= info['uniqueid']	# unique id
        if not prt:
           print ("From OGN DDB:", ogntid, devtype, flarmid, regist, pilot, compid, model, uniqueid) 
        found=True

elif not stealthset:		# deprecated code (used for testing and debugging)

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
        uniqueid= 1
        info    = {'device_id': ogntid, 'device_aprsid':flarmid, 'device_type' : 1, 'registration': regist, 'pilot' : pilot, 'cn': compid, 'aircraft_model' : model}
        print ("From DB:", ogntid, flarmid, regist, pilot, compid, model) # whatch out for multiples Ids !!!!
        print (info)
        if found:		# if found one already ???
           print("WARNING: Multiple IDs for the same tracker !!!! --> ", ID, ogntid)
        found=True
   if not found:
        print ("Device "+ID+" not found on the REG DataBase\n\n")

print( "==============================================================================================\n\n")

if setup or pairing  or stealthset or stealth :		# set the last one !!!

   APP_key=net.TTN_App_Key	# for the $POGNS cmd
   if ttnopt and not helopt:	# if TTN registration
      print ("TheThingsNetwork (TTN) network activity...")

      net.TTN_dev_id      = flarmid.lower()
      net.TTN_dev_Eui     = MAC
      try:
         # add now the TTN V3 
         clicmd = "ttn-lw-cli end-devices delete ogn ogn"+net.TTN_dev_id+" -c .ttn-lw-cli.yml --dev-eui "+net.TTN_dev_Eui+" --join-eui "+net.TTN_joinEui+" " 
         print (clicmd)
         os.system(clicmd)
         clicmd = "ttn-lw-cli end-devices create ogn ogn"+net.TTN_dev_id+" --name OGN"+net.TTN_dev_id.upper()+" -c .ttn-lw-cli.yml --dev-eui "+net.TTN_dev_Eui+" --join-eui "+net.TTN_appEui+" --description OGN/IGC-"+regist+" --frequency-plan-id EU_863_870 --lorawan-version 1.0.3 --lorawan-phy-version 1.0.3-a --root-keys.app-key.key "+net.TTN_app_key
         print (clicmd)
         os.system(clicmd)
      except Exception as e:
         print ("Device:", net.TTN_dev_id, "with MAC:", MAC, "Not registered on the TTN Error: ", e, "\n")

   # end of if ttnopt
# ------------------------------------------------------------------ #
   
   if helopt and not ttnopt:			# if Helium registration
      print ("Helium network activity...")
      net.HEL_dev_id       = flarmid.lower()
      net.HEL_dev_eui      = MAC
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

   if pairing:								# if pairing the OGN TRACKER and a FLARMID ??
      trk=flarmid							# the tracker that we want to pair
      tflarmid=pairing.upper()						# with the flarm device
      localtime = datetime.datetime.now()				# get today's date
      today = localtime.strftime("%y/%m/%d %H:%M:%S")			# in string format yymmdd
      if trk[0:3] != 'OGN' and (tflarmid[0:3] == 'FLR' or tflarmid[0:3] == 'ICA'):
         print ("Pairing error, you can only pair OGN tracker with Flarms")
         conn.close()
         os._exit(-1)

      conn = MySQLdb.connect(host=config.DBhost, user=config.DBuser, passwd=config.DBpasswd, db=DBname, connect_timeout=1000)     # connect with the database
      cursD = conn.cursor()						# connect with the DB set the cursor
      cmd1 = "DELETE FROM "+DBtable+" WHERE id = '"+trk+"' ;"		# delete first from DB
      try:
         cursD.execute(cmd1)						# delete the record on the DB
      except MySQLdb.Error as e:
         print ("SQL error deleting pairing record: ",e, " may be OK or first time\n")
      conn.commit()
      ognreg=getognreg(trk[3:])						# the the information fro the OGN DDB
      flrreg=getognreg(tflarmid[3:])					# glider registration
      cn=getogncn(tflarmid[3:])						# glider competition ID
      model=getognmodel(tflarmid[3:])					# glider model
      if not owner:							# if owner provided ???
         towner="IGC registration"					# dummy owner
      else:
         towner=owner							# use the owner parameter
      if getognchk(trk[3:]) and getognchk(tflarmid[3:]):		# check that both devices are rgistered on the OGN DDB
         cmd1 = "INSERT INTO "+DBtable+" (id, owner, spotid, compid, model, registration, active, devicetype, flarmid) VALUES ( '"+trk+"', '"+towner+"', '"+ognreg+"' , '"+cn+"', '"+model+"', '"+flrreg+"', '1', 'OGNT', '"+tflarmid+"' ) ; "
         print ("Pairing cmd:",cmd1)
         try:
            cursD.execute(cmd1)						# insert the pairing record
         except MySQLdb.Error as e:
            print ("Pairing error, ID already exist on the DB --- SQL error: ",e)
         conn.commit()
      else:
         print ("ADD Pairing Error either the OGN tracker "+trk+" or the FlarmID "+tflarmid+" are not registered on the OGN DDB")
         conn.close()
         os._exit(0)
      print ("PAIRING ==> ", trk, "with FlarmID", tflarmid, ognreg, cn, model, "and owner:", towner, "on DBhost:", config.DBhost, "\n\n")
   # end of if PAIRING

 #------------------------------------------------------------------ #

   if setup:								# if setup is required 
									# use the $POGNS cmd to set the parameters ...
        print("Doing the SETUP of the OGN/IGC Tracker ....\n")
        cmd="$POGNS,Reg="+regist+"\n"					# Registration ID
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,Pilot="+pilot+"\n"					# pilot name
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,ID="+compid+"\n"					# competition ID
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,Model="+model+"\n"					# aircraft model
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,SN="+flarmid+"\n"					# serial number
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,BTname="+flarmid+"\n"				# Bluetooth ID
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,Type="+str(devtype)+"\n"				# device type
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,PilotID="+str(uniqueid)+"\n"			# 
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,Hard="+Hard+"\n"					# Hardware version 
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,Soft="+Soft+"\n"					# Hardware version 
        ser.write(cmd.encode('UTF-8'))
        cmd="$POGNS,PageMask=0x08FF\n"					# Page Mask --> All basic he pages ...
        ser.write(cmd.encode('UTF-8'))

        if APP_key != '':						# if we have an APP key ??
           cmd="$POGNS,AppKey="+APP_key+"\n"
           ser.write(cmd.encode('UTF-8'))

        if stealth:							# if stealth mode requested
           cmd="$POGNS,AddrType=0\n"
           ser.write(cmd.encode('UTF-8'))
           cmd="$POGNS,Stealth=1\n"
           ser.write(cmd.encode('UTF-8'))
           cmd="$POGNS,Reg=0;\n"					# and erase all the data that could identify the tracker
           ser.write(cmd.encode('UTF-8'))
           cmd="$POGNS,Pilot=0;\n"
           ser.write(cmd.encode('UTF-8'))
           cmd="$POGNS,ID=0;\n"
           ser.write(cmd.encode('UTF-8'))
           cmd="$POGNS,Model=0;\n"
           ser.write(cmd.encode('UTF-8'))
           cmd="$POGNS,SN=0;\n"
           ser.write(cmd.encode('UTF-8'))
           cmd="$POGNS,PilotID=0;\n"					# 
           ser.write(cmd.encode('UTF-8'))
           cmd="$POGNS,Base=0;\n"					# 
           ser.write(cmd.encode('UTF-8'))
           cmd="$POGNS,Class=0;\n"					# 
           ser.write(cmd.encode('UTF-8'))
           cmd="$POGNS,Manuf=0;\n"					# 
           ser.write(cmd.encode('UTF-8'))
        elif stealthset:						# if stealth was ON
           cmd="$POGNS,AddrType=3\n"					# back to be a std tracker
           ser.write(cmd.encode('UTF-8'))
           cmd="$POGNS,Stealth=0\n"					# no stealth 
           ser.write(cmd.encode('UTF-8'))
           cmd="$POGNS,Address=0x"+MAC[-6:]+"\n"			# back to the original addr
           ser.write(cmd.encode('UTF-8'))
        ser.write(etx)							# send a Ctrl-C 
        sleep(1)							# wait a second to give a chance to receive the data
        printparams(ser, trkcfg, False) 				# print the new parameters

   if regopt and found:							# if registration on the registration DB
        #print("PPP", MAC, regist, ID, uniqueid, publickey)
        r=setregdata(MAC, regist, ID, uniqueid, publickey)
        print ("Registration at server: ", r)

elif not found:
   print("WARNING: No information about the device "+ID+" on the OGN databases !!!\n\n")
print( "==============================================================================================\n")
ser.close()
os._exit(0)

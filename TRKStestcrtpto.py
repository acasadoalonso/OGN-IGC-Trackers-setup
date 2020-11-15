#!/usr/bin/python3
#########################################################################
# This program receives messages from the OGN/IGC tracker
# OGN/IGC tracker project
#########################################################################
import socket
import string
import time
import sys
import os.path
import psutil
import signal
import atexit
import MySQLdb                          # the SQL data base routines^M
import json
import argparse
from datetime import datetime, timedelta

#########################################################################


def signal_term_handler(signal, frame):
    print('got SIGTERM ... shutdown orderly')
    shutdown() 			# shutdown orderly
    sys.exit(0)


# ......................................................................#
signal.signal(signal.SIGTERM, signal_term_handler)
# ......................................................................#


def prttime(unixtime):
    # get the time from the timestamp
    tme = datetime.utcfromtimestamp(unixtime)
    return(tme.strftime("%H%M%S"))			# the time


#
########################################################################
def shutdown(prt=False):          # shutdown routine, close files and report on activity
                                        # shutdown before exit
	date = datetime.utcnow()        # get the date
	print ("Shutdown now:", date)
	return
########################################################################
#
# --------------------------------------#
def process(msg, prt):
    hn=dd[8:18]+".local"
    try:
       ipAddress   = socket.gethostbyname(hn)
       print(msg, "{} is: {}".format(hn, ipAddress))
    except:
       print(msg, "HN not found", hn)
    return
# --------------------------------------#
# --------------------------------------#
########################################################################
#

programver = 'V1.0'
pidfile="/tmp/TRKScrypto.pid"
print("\n\nStart TRKStest  "+programver)
print("=====================")

print("Program Version:", time.ctime(os.path.getmtime(__file__)))
print("==========================================")
date = datetime.utcnow()                # get the date
dte = date.strftime("%y%m%d")           # today's date
print("\nDate: ", date, "UTC on SERVER:", socket.gethostname(), "Process ID:", os.getpid())
date = datetime.now()			# local time
parser = argparse.ArgumentParser(description="OGN Push to the OGN APRS the delayed tracks")
parser.add_argument('-p',  '--print',     required=False,
                    dest='prt',   action='store', default=False)
args = parser.parse_args()
prt   = args.prt			# print on|off

# --------------------------------------#
#
# get the configuration data
#
# --------------------------------------#
import config                           # get the configuration data
if os.path.exists(pidfile):		# check if another process running
    raise RuntimeError("TRKSTATUS already running !!!")
    exit(-1)
#
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
# --------------------------------------#
# we force everything FALSE as we try to push to the APRS
OGNT        = False

count = 0				# counter of received messages
HOST=""					# localhost
PORT = 50000              		# Arbitrary non-privileged port
hostname = socket.gethostname()		# the hostname to send it back to the client
with open(pidfile, "w") as f:		# set the lock file  as the pid
    f.write(str(os.getpid()))
    f.close()
atexit.register(lambda: os.remove(pidfile))
now=datetime.utcnow()
day=now.day
#########################################################################################
try:					# server process receive the TRKSTATUS messages and store it on the DDBB
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print ("Socket created:") 
    try:
       s.bind((HOST, PORT))
    except:
       time.sleep(30)
       s.bind((HOST, PORT))
    print ("Socket binded:", HOST, PORT) 
    s.listen(1)
    print ("Socket listening:") 
    #socket=s
    conn, addr = s.accept()
    print ("Socket accepted:", addr) 
    sock=conn
    print ("Waiting for connections:", HOST, PORT)
    with conn:
        print('Connected by', addr)
        while True:			# for ever while connected
            now = datetime.utcnow()		# get the UTC time
            if now.day != day:	        # check if day has changed
                print("End of Day...Day: ", day,"\n\n")	# end of UTC day
                shutdown()		# recycle
                print("Bye ... :", count,"\n\n\n")	# end of UTC day
                exit(0)

            data = conn.recv(1024)	# receive the TRKSTATUS message
            if not data: break		# if cancel the client
            count += 1
            dd=data.decode('utf-8')	# convert it to an stream
            if prt:
               print("D:", dd)
					# build the reply msg
            date = datetime.utcnow()                # get the date
            dtetme = date.strftime("%y/%m/%d %H:%M:%S")           # today's date
            msg="OK "+str(count)+" "+dtetme+" "+hostname+" "+programver
            conn.sendall(msg.encode('utf-8')) # send it back to the client
            process(dd,  prt)		# Process the msg
        print ("Counter:", count)
#########################################################################################
except KeyboardInterrupt:
    print("Keyboard input received, end of program, shutdown")
    pass

shutdown()				# shutdown tasks
print ("Exit now ...          ", count)
exit(0)


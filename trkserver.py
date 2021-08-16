#!/usr/bin/python3
#########################################################################
# This program receives the tracker status message from the OGN station and stores them on the MySQL DB
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
from   datetime import datetime, timedelta
from   ognddbfuncs import *

#########################################################################


def signal_term_handler(signal, frame):
    print('got SIGTERM ... shutdown orderly')
    shutdown(cond) 			# shutdown orderly
    sys.exit(0)

def timeout_handler(signum, frame):
        print("Timeout!", file=sys.stderr)
        raise Exception("end of time")

# ......................................................................#
signal.signal(signal.SIGTERM, signal_term_handler)
signal.signal(signal.SIGALRM, timeout_handler)

# ......................................................................#


def prttime(unixtime):
    # get the time from the timestamp
    tme = datetime.utcfromtimestamp(unixtime)
    return(tme.strftime("%H%M%S"))			# the time


#
########################################################################
def shutdown(cond, prt=False):          # shutdown routine, close files and report on activity
                                        # shutdown before exit
	try:
		cond.commit()
		cond.close()
	except:
		print ("Errors at shutdown, ignored ...", file=sys.stderr)
	date = datetime.utcnow()        # get the date
	print ("Shutdown now:", date)
	return
########################################################################
def storedb(curs, data, prt=False):	# store the data on the MySQL DB
	if data[0:2] != 'M:':		# if is is not an status msg, nothing to do
		return ' '
	otime = datetime.utcnow()	# grab the time
	sc1=data[2:].find(':')		# parser the message
	sc2=data[sc1+3:].find(':')
	station=data[2:sc1+2]
	ident="OGN"+data[sc1+3:sc1+sc2+3]
	status=otime.strftime("%H%M%S")+'h '+data[sc1+sc2+4:].rstrip('\n\r ')
	if len(status) > 254:
		status=status[0:254]
	if prt:
		print ("--> S", ident, station, otime, status, "<<<")
					# prepare the SQL command
	inscmd = "insert into OGNTRKSTATUS values ('%s', '%s', '%s', '%s', '%s')" % (ident, station, otime, status, 'STAT')
	try:
		curs.execute(inscmd)	# store the data on the MySQL DB
	except MySQLdb.Error as e:
		try:
			print(">>>MySQL1 Error [%d]: %s" % ( e.args[0], e.args[1]), file=sys.stderr)
		except IndexError:
			print(">>>MySQL2 Error: %s" % str(e), file=sys.stderr)
			print(">>>MySQL3 error:",  numtrksta, inscmd, file=sys.stderr)
			print(">>>MySQL4 data :",  s)
	return ident
#
########################################################################
#

programver = 'V1.1'
pidfile="/tmp/TRKS.pid"
print("\n\nStart TRKSTATUS  "+programver)
print("=====================")

print("Program Version:", time.ctime(os.path.getmtime(__file__)))
print("==========================================")
date = datetime.utcnow()                # get the date
dte  = date.strftime("%y%m%d")          # today's date
print("\nDate: ", date, "UTC on SERVER:", socket.gethostname(), "Process ID:", os.getpid())
date = datetime.now()			# local time
parser = argparse.ArgumentParser(description="OGN Push to the OGN APRS the delayed tracks")
parser.add_argument('-p',  '--print',     required=False,
                    dest='prt',   action='store', default=False)
args  = parser.parse_args()
prt   = args.prt			# print on|off

# --------------------------------------#
#
# get the configuration data
#
# --------------------------------------#
import config                           # get the configuration data
if os.path.exists(pidfile):		# check if another process running
    raise RuntimeError("TRKSERVER already running !!!")
    exit(-1)
#
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
# --------------------------------------#
DBpath      = config.DBpath
DBhost      = config.DBhost
DBuser      = config.DBuser
DBpasswd    = config.DBpasswd
DBname      = config.DBname
# we force everything FALSE as we try to push to the APRS
OGNT        = False
# --------------------------------------#
cond = MySQLdb.connect(host=DBhost, user=DBuser, passwd=DBpasswd, db=DBname)
curs = cond.cursor()               	# set the cursor

print("Time now is: ", date, " Local time")
print("MySQL: Database:", DBname, " at Host:", DBhost)
# --------------------------------------#

count = 0				# counter of received messages
HOST ="ubuntu"			# localhost
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
    s.settimeout(30.0)			# set the timeout 10 seconds
    print ("Socket created:", s.gettimeout()," seconds timeout") 
    signal.alarm(15)		 	# give t 15 seconds to reply
    try:
        try:
           s.bind((HOST, PORT))		# try to bind that port
        except Exception as e:
           print ("Fail BIND once ...", e, file=sys.stderr)
           time.sleep(5)
           s.bind((HOST, PORT))		# try again
    except Exception as to:
           print("BIND timeout ... ", to, file=sys.stderr)
           exit (-1)
    signal.alarm(0)		 	# reset the alarm
    print ("Socket binded:", HOST, PORT) 
    s.listen(1)
    print ("Socket listening:") 
    socket=s
    s.settimeout(None)			# set the timeout none
    try:
       conn, addr = s.accept()
    except Exception as e:
       print ("ACCEPT Exception:", e)
       exit(-3)
    print ("Socket accepted:", addr) 
    sock=conn
    print ("Waiting for connections:", HOST, PORT)
#                                       --------------------------------------------------------
    with conn:
        try:
             h=gethostbyaddr(addr[0])
             print ("Connected to:", addr[0], "Host name:", h[0])
        except:
             print ("Connected to:", addr[0], " that is an unkown host")
        print("Wait now for login from the OGN station and credentials.\n")
        while True:			# for ever while connected
            now = datetime.utcnow()		# get the UTC time
            if now.day != day:	        # check if day has changed
                print("End of Day...Day: ", day,"\n\n")	# end of UTC day
                shutdown(cond)		# recycle
                print("Bye ... :", count,"\n\n\n")	# end of UTC day
                exit(0)

            data = conn.recv(1024)	# receive the TRKSTATUS message
            if not data: break		# if cancel the client
            count += 1
            dd=data.decode('utf-8')	# convert it to an stream
            if prt:
               mm=dd.rstrip(" \n\r")
               print("<-- D:",  mm , ":<<<")
					# build the reply msg
            now = datetime.utcnow()

            id1=storedb(curs, dd, prt)  # store on the DDBB
            reg=getognreg(id1[3:])      # get the registration ID
            cid=getogncn (id1[3:])      # get the competition number
            msg="OK "+str(count)+" "+hostname+' '+programver+' '+reg+' '+' '+cid+' '+now.isoformat()
            conn.sendall(msg.encode('utf-8')) # send it back to the client
            cond.commit()		# and commit it
            if count % 10:
               sys.stdout.flush()
        print ("Counter:", count)
#########################################################################################
except KeyboardInterrupt:
    print("Keyboard input received, end of program, shutdown")
    pass

shutdown(cond)				# shutdown tasks
print ("Exit now ...          ", count)
exit(0)


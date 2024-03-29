#!/usr/bin/pyton3
import socket
import signal
import atexit
import sys
import os
from telnetlib import *
from time import sleep, ctime
import argparse
from datetime import datetime 
#########################################################################
# This script ins installed on the OGN station in order to send the status of the OGN trackers to the management server
#########################################################################


def signal_term_handler(signal, frame):
    print('got SIGTERM ... shutdown orderly')
    sock.close()
    sys.exit(0)
def timout_handler(signum, frame):
        print("Timeout!", file=sys.stderr)
        raise Exception("end of time")

# ......................................................................#
signal.signal(signal.SIGTERM, signal_term_handler)
signal.signal(signal.SIGALRM, timout_handler)
# ......................................................................#
parser = argparse.ArgumentParser(
    description="OGN send info to the management server the OGN tracker status")
parser.add_argument('-p',  '--print',     required=False,
                    dest='prt',   action='store', default=False)
parser.add_argument('-s',  '--server',     required=False,
                    dest='server',   action='store', default='acasado.es')
parser.add_argument('-pt',  '--port',     required=False,
                    dest='port',   action='store', default=50000)
args = parser.parse_args()
prt = args.prt                  # print on|off
server = args.server            # print on|off
port = args.port                # print on|off
programver='V1.1'
pidfile="/tmp/TRK.pid"
print("\n\nStart TRKCLIENT  "+programver)
print("=====================")

print("Program Version:", ctime(os.path.getmtime(__file__)))
print("==========================================")

if os.path.exists(pidfile):             # check if another process running
    raise RuntimeError("TRKCLIENT already running !!!")
    exit(-1)
#
with open(pidfile, "w") as f:           # set the lock file  as the pid
    f.write(str(os.getpid()))
    f.close()
atexit.register(lambda: os.remove(pidfile))

#server="acasado.es"                     # server to send the TRK status messages
server_ip = socket.gethostbyname(server)
print("IP addr: ", server_ip, "for:",server)
hostname = socket.gethostname()          # get the name of the OGN station
print("\nConnecting with:", server, "on port:", port, "from:", hostname)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # create the sock
errorc = 0
while errorc < 1001:                     # while not too many errors
    try:
        sock.connect((server_ip, port))  # try to connect
        break
    except:
        print("Try to connect ...",errorc)
        if errorc == 1000:
            print ("Imposible to connect with:", server_ip," on port:", port, file=sys.stderr)
            exit(-1)
    sleep(5)
    errorc += 1

print("Socket connected to: ", server, ":", port, "from:", hostname)  # report that is connected
# logon to TRKserver now

now = datetime.utcnow()
login = 'L: user '+hostname+' vers '+programver+' '+now.isoformat()# prepare the login message
if prt:
    print(login)
login = login.encode(encoding='utf-8', errors='strict') # convert it to bytes
sock.send(login)                         # send the login
signal.alarm(10)		 	 # give t 10 seconds to reply
try:
    data = sock.recv(1024)               # receive the reply
except:
    print("Time out on first sock.recv ...", file=sys.stderr)
    exit(-2)
signal.alarm(0)				 # reset the alarm
print('--> Received', repr(data))        # and report it
#                                        --------------------------------------
tn = Telnet('localhost', 50001)          # create the telent instance
station = ':'				 # not known station yet
count = 1				 # counter of messages received
sys.stdout.flush()
sys.stderr.flush()
while True:                              # for ever
    try:
        				 # telnet read char by char untile new line
        r = tn.read_until(b'\n').decode('UTF-8')
    except KeyboardInterrupt:            # in case of Crtl-C close
        print("Keyboard input received, end of program, shutdown")
        print("Msgs sent:", count)
        sock.close()
        exit(-3)
    except:                              # any other error
        print("Msgs sent:", count)
        sock.close()
        exit(-4)
    sdr = r.find(">OGNSDR")              # find the TCP/IP indicator
    if sdr > 0:                          # if found
        station = r[8:sdr]               # get the OGN staion name
        print("S:", station, r[sdr+8:].rstrip(" \r\n"))  # report it
        if r[sdr+8] == '>':              # only the status, not the location message
           now = datetime.utcnow()
           login = 'L: station '+station+' vers '+programver+' '+now.isoformat()        # prepare the login station message
           login = login.encode(encoding='utf-8', errors='strict')  # convert it to bytes
           sock.send(login)              # send the login
           data = sock.recv(1024)        # receive the reply
           count += 1
           print('--> Received', repr(data))    # and report it
        continue                         # keep reading chars
#   -------------------------------------
    khz = r.find('kHz')                  # look if it is one of the lines that we need
    if khz == -1:
        continue
    if r[khz+4:khz+6] != '3:':           # it is for a OGN tracker ???
        continue
    ident = r[khz+6:khz+12]              # get the ident
    rr = r[khz+13:]
    sc = rr.find(':')
    body = rr[sc+2:]
    msg = "M:"+station+':'+ident+':'+body
    if prt:
       print("Mesg:", msg)
    msg = msg.encode('utf-8')            # convert to bytes
    if station != ':':			 # if we had alreedy an station info
        try:
            print("<--", msg)
            sock.sendall(msg)            # send it to the management server
        except KeyboardInterrupt:        # if Ctrl-C
            print("Keyboard input received, end of program, shutdown")
            print("Msgs sent:", count)
            sock.close()
            exit(-5)
        except:
            print("Msgs sent:", count)
            sock.close()
            exit(-6)
        signal.alarm(10)		 # give t 10 seconds to reply
        try:
            data = sock.recv(1024)       # receive the ack
            count += 1
            print('--> Received', data.decode('UTF-8'), count)  # and report it
        except:
            print("Time out on sock.recv ...", file=sys.stderr)
        signal.alarm(0)
    sys.stdout.flush()
    sys.stderr.flush()
#########################################################################################################################

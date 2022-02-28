#-------------------------------------
# OGN-SAR Spain interface --- Settings
#-------------------------------------
#
#-------------------------------------
# Setting values
#-------------------------------------
#
import socket
import os
from configparser import ConfigParser
configdir = os.getenv('CONFIGDIR')

if configdir == None and os.name != 'nt':
    configdir = '/etc/local/'
configfile = configdir+'TRKSconfig.ini'
if os.path.isfile("./TRKSconfig.ini"):
    configfile =  './TRKSconfig.ini'
if os.path.isfile(configfile):
	
	# get the configuration parameters
	cfg=ConfigParser()		# get the configuration parameters
	# reading it for the configuration file
	cfg.read(configfile)		# reading it for the configuration file
else:
	print ("Config file: ", configfile, " not found \n")
	exit(-1)
hostname = socket.gethostname()
processid = str(os.getpid())


MySQLtext = cfg.get('server', 'MySQL').strip("'").strip('"')
if (MySQLtext == 'True'):
    MySQL = True
    DBpath = cfg.get('server', 'DBpath').strip("'").strip('"')
    DBhost = cfg.get('server', 'DBhost').strip("'").strip('"')
    DBuser = cfg.get('server', 'DBuser').strip("'").strip('"')
    DBpasswd = cfg.get('server', 'DBpasswd').strip("'").strip('"')
    DBuserread = cfg.get('server', 'DBuserread').strip("'").strip('"')
    DBpasswdread = cfg.get('server', 'DBpasswdread').strip("'").strip('"')
    DBname = cfg.get('server', 'DBname').strip("'").strip('"')
else:
    MySQL = False
LogDatas = cfg.get('server', 'LogData').strip("'").strip('"')
try:
    PIDfile = cfg.get('server', 'pid').strip("'").strip('"')
except:
    PIDfile = '/tmp/APRS.pid'
# --------------------------------------#
if (LogDatas == 'True'):
    LogData = True
else:
    LogData = False

# --------------------------------------#
try:
        prttext     = cfg.get('server', 'prt').strip("'")
        if      prttext == 'True' or prttext == 'ON':
                prt = True
        else:
                prt = False
except:
        prt         = False


try:
    DDBhost = cfg.get('server', 'DDBhost').strip("'")
except:
    DDBhost = 'acasado.es'

try:
    DDBport = cfg.get('server', 'DDBport').strip("'")
except:
    DDBport = '60082'

try:
    DDBurl1 = cfg.get('server', 'DDBurl1').strip("'")
except:
    DDBurl1 = 'http://acasado.es:60082/download/?j=2'

try:
    DDBurl2 = cfg.get('server', 'DDBurl2').strip("'")
except:
    DDBurl2 = 'http://DDB.glidernet.org/download/?j=2'



# report the configuration paramenters
LogData = False
if 'USER' in os.environ and prt:

   print("Hostname:            ", hostname, " and config file: ", configfile, "process ID:",processid)
   if MySQL:
      print("Config server values:",                  "MySQL =", MySQL, DBhost, DBuser, DBname, DBpath)
# --------------------------------------#
APP = 'TRKSETUP'					# alternate TRK SETUP
SOCK = 0
SOCK_FILE = 0
RegWarning = True

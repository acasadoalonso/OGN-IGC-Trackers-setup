# OGN-IGC-Trackers-setup
OGN/IGC Trackers setup utilities 

This is a set of utilities to do the setup of OGN/IGC tracker for WGC.

The main utility is the trksetup.py
Invokation   python3 trksetup -h      or     ./trksetup.py -h



OGN tracker setup program:
It gets the information from the tracker firmware and hendles the setup parameter.
The tracker mus be connected to the USB port.
==================================================================================


Hostname:             CASADOUBUNTU  and config file:  ./TRKSconfig.ini 14475
Config server values: MySQL = True CASADOUBUNTU ogn APRSLOG /nfs/OGN/SWdata/
usage: trksetup.py [-h] [-p PRT] [-u USB] [-s SETUP] [-k KEYS] [-kf KEYFILE]
                   [-o OGNDDB] [-t TTN] [-n NOENCR]

OGN manage the OGN TRACKERS setup parameters

optional arguments:
  -h, --help            show this help message and exit
  -p PRT, --print PRT
  -u USB, --usb USB
  -s SETUP, --setup SETUP
  -k KEYS, --printkeys KEYS
  -kf KEYFILE, --keyfile KEYFILE
  -o OGNDDB, --ognddb OGNDDB
  -t TTN, --ttn TTN
  -n NOENCR, --noencrypt NOENCR


the optional parameters are:

-p or --print 		for display on stdout the results
-u or --usb USB0	Indicate the USB port, the default is USB0
-s or --setup True	To indicate to do the setup of the new parameters
-k or --keys True	To get the encryption keys
-kf or --keyfile nnn	It is the name of the file containing the keys
-o or --ognddn True	To use the OGN DDB as the base for geting the information about the tracker
-t or --ttn True	To do the setup on the LoRaWan network thethingsnetwork.org 
-n or --noencr		To indicate that no encrytion is needed





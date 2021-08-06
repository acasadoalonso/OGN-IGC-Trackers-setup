#!/bin/bash
#
# -h, --help            show this help message and exit
# -p PRT, --print PRT
# -u USB, --usb USB
# -s SETUP, --setup SETUP
# -k KEYS, --printkeys KEYS
# -kf KEYFILE, --keyfile KEYFILE
# -o OGNDDB, --ognddb OGNDDB
# -t TTN, --ttn TTN
# -m HELIUM, --helium HELIUM
# -n ENCR, --encrypt ENCR
# -r REG, --register REG
# -g PAIR --pairing PAIRING
# -w owner --owner OWNER
if [ $# == 2 ]
then
   python3 trksetup.py --print True --setup True --printkeys False --ognddb True --encrypt False --ttn False --pairing $1 --owner $2
elif [ $# == 1 ]
then
   python3 trksetup.py --print True --setup True --printkeys False --ognddb True --encrypt False --ttn False --pairing $1 
else
   python3 trksetup.py --print True --setup True --printkeys False --ognddb True --encrypt False --ttn False 
fi

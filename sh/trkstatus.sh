#!/bin/bash
SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`

cd /nfs/OGN/SWdata 
echo "========"$(hostname)"===============:"	>>trks.log
date                            		>>trks.log
python3 ~/src/APRSsrc/main/APRScalsunrisesunset.py >>trks.log
echo "TRKserver.sh:"	            		>>trks.log
echo "============:"     	       		>>trks.log
python3 $SCRIPTPATH/../trkserver.py -p True	>>trks.log 2>>trks.log &
pgrep -a python3				>>trks.log
date                            		>>trks.log
cd

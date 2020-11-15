#!/bin/bash
pid=$"/tmp/TRKS.pid"
pnum=$(pgrep -x -f "python3 /home/angel/src/TRKSsrc/main/trkserver.py -p True")
if [ $? -eq 0 ]
then
        logger -t $0 "TRKServer is running..."$pnum
else
        if [ -f $pid ] # if TRK server is  not running
        then
       			pnum=$(cat $pid)
                        sudo kill $pnum >/dev/null 2>/dev/null
                        rm $pid 
        fi

        logger -t $0 "TRKserver is restarting"
        bash ~/src/TRKSsrc/sh/trkstatus.sh
fi


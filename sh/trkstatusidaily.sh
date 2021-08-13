#!/bin/bash
cd /nfs/OGN/SWdata 
echo "========"$(hostname)"===============:"	>>trks.log
date                            		>>trks.log
pgrep -a python3				>>trks.log
if [ $# = 0 ]; then
        server='localhost'
else
        server=$1
fi
hostname=$(hostname)

if [ -z $CONFIGDIR ]
then 
     export CONFIGDIR=/etc/local/
fi
DBuser=$(echo    `grep '^DBuser '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBuser //g')
DBpasswd=$(echo  `grep '^DBpasswd ' $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpasswd //g' | sed 's/ //g' )
DBpath=$(echo    `grep '^DBpath '   $CONFIGDIR/APRSconfig.ini` | sed 's/=//g' | sed 's/^DBpath //g' | sed 's/ //g' )

cd $DBpath
date                                                                                               >>trks.log 2>/dev/null
echo "Server: "$server                                                                             >>trks.log 
day=$(date +%d)
mon=$(date +%m)
yea=$(date +%y)
if   [ $day = "08" ]; then
        day="07"
elif [ $day = "09" ]; then
        day="08"
elif [ $day = "10" ]; then
        day="09"
else
        let "day = $day - 1"
fi
if [   $day = "7" ]; then
        day="07"
elif [ $day = "6" ]; then
        day="06"
elif [ $day = "5" ]; then
        day="05"
elif [ $day = "4" ]; then
        day="04"
elif [ $day = "3" ]; then
        day="03"
elif [ $day = "2" ]; then
        day="02"
elif [ $day = "1" ]; then
        day="01"
fi

date=$yea$mon$day
echo $date							>>trks.log 
cd $DBpath
date                                                              >>trks.log 2>/dev/null
echo "clean OGNDATA in APRSLOG"                                   >>trks.log 2>/dev/null
echo "DELETE FROM OGNTRKSTATUS WHERE otime < date('"$(date +%Y-%m-%d)"')-1; " | mysql -u $DBuser -p$DBpasswd -v -h $server APRSLOG >>trks.log 2>/dev/null
echo "SELECT COUNT(*) from OGNTRKSTATUS  ; "  | mysql -u $DBuser -p$DBpasswd -v -h $server APRSLOG     >>trks.log 2>/dev/null
date                                                              >>trks.log 2>/dev/null

date                            		>>trks.log
mv trks.log archive/trks$(date +%y%m%d).log 
mv trkserr.log archive/trkserr$(date +%y%m%d).log 
cd

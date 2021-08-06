#!/bin/bash
cd /nfs/OGN/SWdata 
echo "========"$(hostname)"===============:"	>>trks.log
date                            		>>trks.log
pgrep -a python3				>>trks.log
date                            		>>trks.log
mv trks.log archive/trks$(date +%y%m%d).log 
cd

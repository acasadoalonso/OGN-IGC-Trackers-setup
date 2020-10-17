rm *funcs.py 
ln -s ../funcs/ognddbfuncs.py .
ln -s ../funcs/pkcsfuncs.py .
rm trkstatus*
ln -s /var/www/html/node/trkstatus* .
ls -la *funcs.py trkstatus*

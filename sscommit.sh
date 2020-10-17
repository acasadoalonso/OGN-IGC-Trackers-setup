rm *funcs.py 
cp /nfs/OGN/src/funcs/ognddbfuncs.py .
cp /nfs/OGN/src/funcs/pkcsfuncs.py .
rm trkstatus*
cp /var/www/html/node/trkstatus*     .
git add .
git commit
git push origin main

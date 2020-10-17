#
def getkeys(DecKey, key):
	DecKey.append(int(key[0:8],16))
	DecKey.append(int(key[8:16],16))
	DecKey.append(int(key[16:24],16))
	DecKey.append(int(key[24:32],16))
	return(DecKey)
def getkeyfile(keyfile):
	with open(keyfile, mode='rb') as keyfile:
     		key = keyfile.read()
	return(key)
def getdeckey(keyfile):
	key=getkeyfile(keyfile)
	DECKEY=b''
	idx=0
	while idx < 16:
		k=key[idx*2: idx*2+2].decode('utf-8')
		kk = int(str(k), 16)
		kkk=chr(kk).encode('utf-8')
		DECKEY += kkk
		idx += 1
	return(DECKEY)
##########

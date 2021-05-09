#
import rsa


def getkeys(DecKey, key):
    DecKey.append(int(key[0:8], 16))
    DecKey.append(int(key[8:16], 16))
    DecKey.append(int(key[16:24], 16))
    DecKey.append(int(key[24:32], 16))
    return(DecKey)


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

# #########


def getkeyfromencryptedfile(kfile, privkey):
    with open(kfile, mode='rb') as keyfile:
        key = keyfile.read()
    return (rsa.decrypt(key, privkey))


def getprivatekey(pem):

    with open(pem, mode='rb') as privatefile:
        keydata = privatefile.read()
    privkey = rsa.PrivateKey.load_pkcs1(keydata)
    return(privkey)


def getpublickey(pem):
    with open(pem, mode='rb') as privatefile:
        keydata = privatefile.read()
    publkey = rsa.PublicKey.load_pkcs1(keydata)
    return(publkey)


def getkeyfile(keyfile):
    with open(keyfile, mode='rb') as keyfile:
        key = keyfile.read()
    return(key)


def getsignature(key, pem):
    privkey=getprivatekey(pem)
    signature=rsa.sign(key, privkey, 'SHA-1')
    return(signature)

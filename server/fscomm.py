# fscomm - filesystem based communication
# code by Albert Zeyer, www.az2000.de
# 2012-06-08

import os
basedirs = None

def checkDropbox():
	assert os.path.exists(os.path.expanduser("~/.Dropbox"))

def setup(appid):
	checkDropbox()
	global basedirs
	basedirs = ["~/Dropbox/.AppCommunication/" + appid]

class Dev:
	def __init__(self, publicKey):
		self.publicKey = publicKey

	def __hash__(self):
		return hash(self.devId)
	def __cmp__(self, other):
		return cmp(self.publicKey, other.publicKey)

def readPublicKey(fn):
	return open(fn).read()

def devices():
	devs = set()
	for basedir in basedirs:
		try: devdirs = os.listdir(basedir)
		except: continue
		for devdir in devdirs:
			if os.path.isdir(devdir) and os.path.exists(devdir + "/publicKey"):
				publicKey = readPublicKey(fn)
				d = Dev(publicKey)
				devs.insert(d)
	for d in devs:
		yield d

def dev(publicKey):
	return Dev(publicKey)

def wait():
	# stupid for now...
	import time
	time.sleep(10)
	# do pyinotify or so later...

def randomString(l):
	import random
	return ''.join(chr(random.randint(0, 0xFF)) for i in range(l))

def genkeypair():
	from Crypto.PublicKey import RSA
	key = RSA.generate(2048)
	pubkey = key.publickey().exportKey("DER")
	privkey = key.exportKey("DER")
	return (pubkey,privkey)
	
def encrypt(v, rsapubkey):
	from Crypto.PublicKey import RSA
	rsakey = RSA.importKey(rsapubkey)
	from Crypto.Cipher import PKCS1_OAEP
	rsa = PKCS1_OAEP.new(rsakey)
	import binstruct
	from array import array
	aeskey = randomString(32)
	iv = randomString(16)
	from Crypto.Cipher import AES
	aes = AES.new(aeskey, AES.MODE_CBC, iv)
	data = binstruct.varEncode(v)
	data += array("B", (0,) * (-len(data) % 16))
	out = binstruct.strEncode(rsa.encrypt(aeskey + iv))
	out += array("B", aes.encrypt(data))
	return out

def decrypt(stream, rsaprivkey):
	from array import array
	from StringIO import StringIO
	if isinstance(stream, array): stream = stream.tostring()
	if isinstance(stream, str): stream = StringIO(stream)
	from Crypto.PublicKey import RSA
	rsakey = RSA.importKey(rsaprivkey)
	from Crypto.Cipher import PKCS1_OAEP
	rsa = PKCS1_OAEP.new(rsakey)
	import binstruct
	aesdata = binstruct.strDecode(stream)
	aesdata = rsa.decrypt(aesdata)
	aeskey = aesdata[0:32]
	iv = aesdata[32:]
	from Crypto.Cipher import AES
	aes = AES.new(aeskey, AES.MODE_CBC, iv)
	class Stream:
		buffer = []
		def read1(self):
			if len(self.buffer) == 0:
				nextIn = stream.read(16)
				self.buffer += list(aes.decrypt(nextIn))
			return self.buffer.pop(0)
		def read(self, n):
			return "".join([self.read1() for i in range(n)])
	v = binstruct.varDecode(Stream())
	return v

# TODO ...

def addsignature(data, rsaprivkey):
	if isinstance(data, str): data = array("B", data)
	if isinstance(data, unicode): data = array("B", data.encode("utf-8"))
	from Crypto.PublicKey import RSA
	rsakey = RSA.importKey(rsaprivkey)
	from Crypto.Signature import PKCS1_PSS
	pss = PKCS1_PSS.new(rsakey)
	from Crypto.Hash import SHA512
	h = SHA512.new()
	h.update(data.tostring())
	sign = pss.sign(h)
	import binstruct
	return binstruct.strEncode(sign) + data

def verifysignature(stream, rsapubkey):
	if isinstance(data, str): data = array("B", data)
	if isinstance(data, unicode): data = array("B", data.encode("utf-8"))
	import binstruct
	
	from Crypto.PublicKey import RSA
	rsakey = RSA.importKey(rsapubkey)
	from Crypto.Signature import PKCS1_PSS
	pss = PKCS1_PSS.new(rsakey)
	from Crypto.Hash import SHA512
	h = SHA512.new()
	h.update(data.tostring())

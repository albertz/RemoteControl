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


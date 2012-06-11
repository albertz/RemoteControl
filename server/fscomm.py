# fscomm - filesystem based communication
# code by Albert Zeyer, www.az2000.de
# 2012-06-08

import os
import binstruct
basedirs = None

def checkDropbox():
	assert os.path.exists(os.path.expanduser("~/.Dropbox"))

def setup(appid):
	checkDropbox()
	global basedirs
	basedirs = ["~/Dropbox/.AppCommunication/" + appid]

class Dev:
	def __init__(self, devId, publicKeys):
		self.devId = devId
		self.publicKeys = publicKeys
	def __hash__(self):
		return hash(self.devId)
	def __cmp__(self, other):
		return cmp(self.publicKey, other.publicKey)

	def awaitingConnections(): pass
	def connections(): pass
	
class Conn:
	pass

def readPublicKeys(fn):
	return binstruct.read(fn)

def devices():
	devs = set()
	for basedir in basedirs:
		try: devdirs = os.listdir(basedir)
		except: continue
		for devdir in devdirs:
			keysFn = devdir + "/publicKeys"
			if os.path.isdir(devdir) and os.path.exists(keysFn):
				devId = os.path.basename(devdir)
				publicKeys = readPublicKeys(keysFn)
				d = Dev(devId, publicKeys)
				devs.insert(d)
	for d in devs:
		yield d

def dev(publicKeys):
	return Dev(publicKeys)

def wait():
	# stupid for now...
	import time
	time.sleep(10)
	# do pyinotify or so later...


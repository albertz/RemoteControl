# fscomm - filesystem based communication
# code by Albert Zeyer, www.az2000.de
# 2012-06-08

import os
import binstruct
from glob import glob
basedirs = None
localDev = None

def checkDropbox():
	assert os.path.exists(os.path.expanduser("~/Dropbox"))

def setup(appid, _localDev):
	global basedirs, localDev
	checkDropbox()
	basedirs = ["~/Dropbox/.AppCommunication/" + appid]
	localDev = _localDev
	
def findFn(fn):
	for d in basedirs:
		if os.path.exists(d + "/" + fn):
			return d + "/" + fn
	return None

def baseDirFor(fn):
	for d in basedirs:
		if os.path.exists(d + "/" + fn):
			return d
	return None

def existsFn(fn):
	return bool(baseDirFor(fn))
	
class Dev:
	def __init__(self, devId, publicKeys=None):
		self.devId = devId
		if publicKeys:
			self.publicKeys = publicKeys
		if not self.publicKeys:
			self.publicKeys = readPublicKeys(findFn(devId))
	
	def __getattr__(self, key):
		if key == "publicKeys":
			self.publicKeys = readPublicKeys(findFn(devId))
			return self.publicKeys
		raise AttributeError("no attrib '%s'" % key)
		
	def __hash__(self):
		return hash(self.devId)
	def __cmp__(self, other):
		return cmp(self.publicKeys.sign, other.publicKeys.sign)

	def connDirs(self):
		for d in basedirs:
			devDir = d + "/" + self.devId
			for connd in glob(devDir + "/messages-from-*"):
				yield connd
	def connections(self):
		for d in self.connDirs():
			sourceDevId = os.path.basename(d)[len("messages-from-"):]
			for connf in glob(d + "/channel-*-init"):
				connId = os.path.basename(connf)[:-5]
				yield Conn(self.devId, sourceDevId, connId)
	def awaitingConnections(self):
		for c in self.connections():
			pass
	
class Conn:
	def __init__(self, dstDevId, srcDevId, connId):
		self.dstDev = Dev(dstDevId)
		self.srcDev = Dev(srcDevId)
		self.baseDir = baseDirFor(self.initFn())
		self.connId = connId
		self.connData = self.readFileSrcToDst(self.initFn())
		self.srcToDstSeqnr = 1
		self.dstToSrcSeqnr = 1		
	def srcToDstPrefixFn(self):
		return self.dstDevId + "/messages-from-" + self.srcDevId + "/" + self.connId
	def dstToSrcPrefixFn(self):
		return self.dstDevId + "/messages-to-" + self.srcDevId + "/" + self.connId
	def readFileSrcToDst(self, fullfn):
		global localDev
		assert self.dstDev == localDev
		dstPrivKey = localDev.privateKeys.crypt
		srcPubKey = self.srcDev.publicKeys.sign
		return binstruct.readDecrypt(fullfn, dstPrivKey, srcPubKey)
	def writeFileDstToSrc(self, fullfn, v):
		global localDev
		assert self.dstDev == localDev
		srcPubKey = self.srcDev.publicKeys.crypt
		dstPrivKey = localDev.privateKeys.sign
		return binstruct.writeEncrypt(fullfn, v, srcPubKey, dstPrivKey)
	def initFn(self):
		return self.srcToDstPrefixFn() + "-init"
	def ackFn(self):
		return self.srcToDstPrefixFn() + "-ack"		
	def refusedFn(self):
		return self.srcToDstPrefixFn() + "-refused"
	
	def accept(self):
		open(self.baseDir + "/" + self.ackFn(), "w").close()
	def refuse(self, reason):
		fullfn = self.baseDir + "/" + self.refusedFn()
		self.writeFileDstToSrc(fullfn, {"reason":reason})

	def readPackages(self):
		while True:
			fn = self.baseDir + "/" + self.srcToDstPrefixFn() + "-" + str(self.srcToDstSeqnr)
			if not os.path.exists(fn): break
			pkg = binstruct.Dict()
			pkg.seqnr = self.srcToDstSeqnr
			pkg.data = self.readFileSrcToDst(fn)
			open(fn + "-ack", "w").close()
			self.srcToDstSeqnr += 1
			yield pkg

	def sendPackage(self, pkg):
		fullfn = self.baseDir + "/" + self.dstToSrcPrefixFn() + "-" + str(self.dstToSrcSeqnr)
		self.writeFileDstToSrc(fullfn, pkg)
		self.dstToSrcSeqnr += 1
		
def readPublicKeys(fn):
	keys = binstruct.read(fn)
	assert isinstance(keys, dict)
	assert "crypt" in keys
	assert "sign" in keys
	return keys

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


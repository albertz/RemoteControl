# fscomm - filesystem based communication
# code by Albert Zeyer, www.az2000.de
# 2012-06-08

import os
import binstruct
from glob import glob
import itertools
import random

basedirs = None
localDev = None

def checkDropbox():
	assert os.path.exists(os.path.expanduser("~/Dropbox"))

def setup(appid, _localDev):
	global basedirs, localDev
	checkDropbox()
	basedirs = [os.path.expanduser("~") + "/Dropbox/.AppCommunication/" + appid]
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
	
	def __getattr__(self, key):
		if key == "publicKeys":
			self.publicKeys = readPublicKeys(findFn(devId))
			return self.publicKeys
		for key in ("type", "appInfo"):
			value = binstruct.readDecrypt(
				findFn(self.devId + "/" + key),
				verifysign_rsapubkey = self.publicKeys.sign)
			setattr(self, key, value)
			return value
		raise AttributeError("no attrib '%s'" % key)
	
	def __str__(self):
		return "<Dev %s>" % self.devId	
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
			if c.isAwaiting():
				yield c

def commonStrLen(*args):
	c = 0
	for cs in itertools.izip(*args):
		if min(cs) != max(cs): break
		c += 1
	return c

class LList: # lazy list
	def __init__(self, base, op=iter):
		self.base = base
		self.op = op
	def __add__(self, other):
		return LList((self, other), lambda x: itertools.chain(*x))
	def __iter__(self):
		return self.op(self.base)
	def __str__(self):
		return "LList(%s,%s)" % (self.base, self.op)
	def __getslice__(self, start, end):
		# slow dummy implementation
		if start is None: start = 0
		tmp = None
		for i, v in itertools.izip(itertools.count(0), iter(self)):
			if i >= end: break
			if i == start: tmp = v
			if i > start: tmp += v
		return tmp

class LFSeq: # lazy infinite sequence with new elements from func
	def __init__(self, func):
		self.evaluated = []
		self.func = func
	def fillUpToLen(self, n):
		self.evaluated += [self.func() for i in range(len(self.evaluated), n)]
	def __iter__(self):
		i = 0
		while True:
			yield self[i]
			i += 1
	def __getitem__(self, i):
		self.fillUpToLen(i + 1)
		return self.evaluated[i]
	def __getslice__(self, i, k):
		assert k is not None, "inf not supported here" # (would be easy via LList, though...)
		if i is None: i = 0
		assert i >= 0, "LFSeq has no len"
		assert k >= 0, "LFSeq has no len"
		self.fillUpToLen(k)
		return self.evaluated[i:k]

chars = map(chr, range(ord("a"), ord("z")) + range(ord("0"),ord("9")))
rndChar = lambda: random.choice(chars)
LRndSeq = lambda: LFSeq(rndChar)

def registerDev(dev):
	"""returns existing matching Dev, if there is any
	otherwise, it creates a new Dev"""
	assert "privateKeys" in dev
	assert "publicKeys" in dev
	assert "appInfo" in dev
	assert "type" in dev
	
	from sha import sha
	longDevId = LList("dev-" + sha(dev["publicKeys"]["sign"]).hexdigest()) + "-" + LRndSeq()
	longestCommonDevId = 9
	takenDevIds = set()
	for d in devices():
		if d.publicKeys == dev["publicKeys"]:
			# update if needed
			for key,value in dev.items():
				setattr(d, key, value)
			return d
		takenDevIds.add(d.devId)
		longestCommonDevId = max(longestCommonDevId, commonStrLen(longDevId, d.devId))
	devId = longDevId[:longestCommonDevId+1]
	
	# create new
	devdir = basedirs[0] + "/" + devId
	os.makedirs(devdir)
	binstruct.write(devdir + "/publicKeys", dev["publicKeys"])
	for key in ("appInfo","type"):
		binstruct.writeEncrypt(
			devdir + "/" + key, dev[key],
			sign_rsaprivkey = dev["privateKeys"]["sign"])
	newdev = Dev(devId, binstruct.Dict(dev["publicKeys"]))
	for key,value in dev.items():
		setattr(newdev, key, value)
	return newdev

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
	def isAwaiting(self):
		exAck = os.path.exists(self.baseDir + "/" + self.ackFn())
		exRefused = os.path.exists(self.baseDir + "/" + self.refusedFn())
		return not exAck and not exRefused
	
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
			devdir = basedir + "/" + devdir
			keysFn = devdir + "/publicKeys"
			if os.path.isdir(devdir) and os.path.exists(keysFn):
				devId = os.path.basename(devdir)
				publicKeys = readPublicKeys(keysFn)
				d = Dev(devId, publicKeys)
				devs.add(d)
	for d in devs:
		yield d

def dev(publicKeys):
	return Dev(publicKeys)

def wait():
	# stupid for now...
	import time
	time.sleep(10)
	# do pyinotify or so later...


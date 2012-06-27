# fscomm - filesystem based communication
# code by Albert Zeyer, www.az2000.de
# 2012-06-08

import time
import binstruct
import itertools, random, re

class FS:
	def open(self, fn): raise NotImplemented
	def openW(self, fn): raise NotImplemented
	def remove(self, fn): raise NotImplemented
	def mkdir(self, fn): raise NotImplemented
	def exists(self, fn): raise NotImplemented
	def isdir(self, fn): raise NotImplemented
	def listdir(self, fn): raise NotImplemented

	def makedirs(self, fn):
		splitted = fn.split("/")
		for i in range(1, len(splitted)+1):
			d = "/".join(splitted[0:i])
			if not self.exists(d) or not self.isdir(d):
				self.mkdir(d)
	def rmtree(self, fn):
		if self.isdir(fn):
			for f in self.listdir(fn):
				self.rmtree(fn + "/" + f)
		else:
			self.remove(fn)
	def glob(self, pattern):
		from fnmatch import fnmatch
		splitted = pattern.split("/")
		def _glob(basedir, patternlist):
			basepattern = patternlist[0]
			rest = patternlist[1:]
			if "*" in basepattern or "?" in basepattern:
				l = []
				for f in self.listdir(basedir + "/."):
					if fnmatch(f, basepattern):
						if rest:
							l += _glob(basedir + f + "/", rest)
						else:
							l += [basedir + f]
				return l
			else: # basepattern not a pattern
				if not self.exists(basedir + basepattern): return []
				if rest:
					return _glob(basedir + basepattern + "/", rest)
				else:
					return [basedir + basepattern]
		return _glob("", splitted)
	def dirname(self, fn):
		import os
		return os.path.dirname(fn)
	def basename(self, fn):
		import os
		return os.path.basename(fn)		
		
class LocalFS(FS):
	import os
	def __init__(self, basedir): self.basedir = basedir
	def open(self, fn): return open(self.basedir + "/" + fn)
	def openW(self, fn): return open(self.basedir + "/" + fn, "w")
	def remove(self, fn): return self.os.remove(self.basedir + "/" + fn)
	def mkdir(self, fn): self.os.mkdir(self.basedir + "/" + fn)
	def exists(self, fn): return self.os.path.exists(self.basedir + "/" + fn)
	def isdir(self, fn): return self.os.path.isdir(self.basedir + "/" + fn)
	def listdir(self, fn): return self.os.listdir(self.basedir + "/" + fn)

class DropboxFS(FS):
	def __init__(self, basedir):
		self.basedir = basedir
		
		import dropboxfs
		self.dropboxClient = dropboxfs.Client()

		def get_func_wrapper(fn):
			f = getattr(self.dropboxClient, fn)
			def func_wrapper(filename):
				#print "called func wrapper", fn, filename
				return f(self.basedir + "/" + filename)			
			return func_wrapper
		
		for fn in ["open","openW","remove","mkdir","exists","isdir","listdir"]:
			setattr(self, fn, get_func_wrapper(fn))
			
fs = None
localDev = None

def checkLocalDropbox():
	import os
	assert os.path.exists(os.path.expanduser("~/Dropbox"))

def setup(appid, _localDev, useDropboxOnline=True):
	global fs, localDev
	localDev = _localDev
	if useDropboxOnline:
		fs = DropboxFS(".AppCommunication/" + appid)
	else:
		checkLocalDropbox()
		import os
		fs = LocalFS(os.path.expanduser("~") + "/Dropbox/.AppCommunication/" + appid)
	
class Dev:
	def __init__(self, devId, publicKeys=None):
		self.devId = devId
		if publicKeys:
			self.publicKeys = publicKeys
	
	def __getattr__(self, key):
		if key == "publicKeys":
			self.publicKeys = readPublicKeys(self.devId + "/publicKeys")
			return self.publicKeys
		if key in ("type", "appInfo", "name"):
			value = binstruct.readDecrypt(
				fs.open(self.devId + "/" + key),
				verifysign_rsapubkey = self.publicKeys.sign)
			setattr(self, key, value)
			return value
		raise AttributeError("no attrib '%s'" % key)
	
	def __repr__(self):
		return "<Dev %s>" % self.devId	
	def __hash__(self):
		return hash(self.devId)
	def __cmp__(self, other):
		return cmp(self.publicKeys.sign, other.publicKeys.sign)

	def user_string(self):
		return "Device " + self.name

	def connections(self): # from the server-side
		r = re.compile("^.*/messages-(to|from)-(.*)/channel-([A-Za-z0-9]+)-(.*)$")
		conns = set()
		for d in fs.glob(self.devId + "/messages-*/channel-*"):
			m = r.match(d)
			if not m:
				print "strange msg dir:", d
				fs.rmtree(d)
				continue
			msgDir,msgDevId,connIdNr,connTag = m.groups()
			conns.add((msgDevId,connIdNr))
		for msgDevId,connIdNr in conns:
			if not fs.glob(msgDevId):
				print "strange dev src, not existing:", msgDevId
				for f in fs.glob(self.devId + "/messages-*-" + msgDevId):
					fs.rmtree(f)
				continue
			if not fs.glob(self.devId + "/messages-from-" + msgDevId + "/channel-" + connIdNr + "-*"):
				print msgDevId + "/channel-" + connIdNr + " has no msgs-from"
				for f in fs.glob(self.devId + "/messages-to-" + msgDevId + "/channel-" + connIdNr + "-*"):
					fs.remove(f)
				continue
			if not fs.glob(self.devId + "/messages-from-" + msgDevId + "/channel-" + connIdNr + "-init"):
				print msgDevId + "/channel-" + connIdNr + " has no init"
				for f in fs.glob(self.devId + "/messages-*-" + msgDevId + "/channel-" + connIdNr + "-*"):
					fs.remove(f)
				continue			
			connId = "channel-" + connIdNr
			sourceDevId = msgDevId
			yield Conn(self, Dev(sourceDevId), connId, isClient=False)
			
	def awaitingConnections(self):
		for c in self.connections():
			if c.isAwaiting():
				yield c

	def connectFrom(self, srcDev, connData):
		assert "intent" in connData
		connd = self.devId + "/messages-from-" + srcDev.devId
		try: fs.mkdir(connd)
		except: pass # might exist
		connIdNum = LRndSeq()
		for i in itertools.count(4):
			connId = "channel-" + connIdNum[:i]
			channelfn = connd + "/" + connId + "-init"
			if fs.exists(channelfn): continue
			binstruct.writeEncrypt(
				fs.openW(channelfn), connData,
				encrypt_rsapubkey = self.publicKeys.crypt,
				sign_rsaprivkey = srcDev.privateKeys.sign).close()
			return Conn(self, srcDev, connId, isClient=True)

	def storeData(self, srcDev, fn, data):
		datad = self.devId + "/data-from-" + srcDev.devId
		try: fs.mkdir(datad)
		except: pass
		binstruct.writeEncrypt(
			fs.openW(datad + "/" + fn), data,
			encrypt_rsapubkey = self.publicKeys.crypt,
			sign_rsaprivkey = srcDev.privateKeys.sign).close()
	
	def loadData(self, srcDev, fn):
		datad = self.devId + "/data-from-" + srcDev.devId
		return binstruct.readDecrypt(
			fs.open(datad + "/" + fn),
			decrypt_rsaprivkey = self.privateKeys.crypt,
			verifysign_rsapubkey = srcDev.publicKeys.sign)
		
	
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
		if isinstance(self.evaluated[0], basestring):
			return "".join(self.evaluated[i:k])
		else:
			return self.evaluated[i:k]

chars = map(chr, range(ord("a"), ord("z")) + range(ord("0"),ord("9")))
rndChar = lambda: random.choice(chars)
LRndSeq = lambda: LFSeq(rndChar)

def localDevName():
	import os
	uname = os.uname()
	return uname[1] + " on " + uname[0] + " " + uname[2] + " " + uname[4]

def registerDev(dev):
	"""returns existing matching Dev, if there is any
	otherwise, it creates a new Dev"""
	assert "privateKeys" in dev
	assert "publicKeys" in dev
	assert "appInfo" in dev
	assert "type" in dev
	global localDev
	
	from sha import sha
	longDevId = LList("dev-" + sha(dev["publicKeys"]["sign"]).hexdigest()) + "-" + LRndSeq()
	longestCommonDevId = 9
	takenDevIds = set()
	for d in devices():
		if d.publicKeys == dev["publicKeys"]:
			# update if needed
			for key,value in dev.items():
				if isinstance(value, dict): value = binstruct.Dict(value)
				setattr(d, key, value)
			if localDev.publicKeys["sign"] == d.publicKeys["sign"]:
				localDev = d
			return d
		takenDevIds.add(d.devId)
		longestCommonDevId = max(longestCommonDevId, commonStrLen(longDevId, d.devId))
	devId = longDevId[:longestCommonDevId+1]
	
	# create new
	devdir = devId
	fs.makedirs(devdir)
	binstruct.write(fs.openW(devdir + "/publicKeys"), dev["publicKeys"]).close()
	for key in ("appInfo","type"):
		binstruct.writeEncrypt(
			fs.openW(devdir + "/" + key), dev[key],
			sign_rsaprivkey = dev["privateKeys"]["sign"])
	newdev = Dev(devId, binstruct.Dict(dev["publicKeys"]))
	for key,value in dev.items():
		if isinstance(value, dict): value = binstruct.Dict(value)
		setattr(newdev, key, value)
	binstruct.writeEncrypt(
		fs.openW(devdir + "/name"), localDevName(),
		sign_rsaprivkey = dev["privateKeys"]["sign"])
	if localDev.publicKeys["sign"] == newdev.publicKeys["sign"]:
		localDev = newdev
	return newdev

class Conn:
	def __init__(self, dstDev, srcDev, connId, isClient):
		global localDev
		self.dstDev = dstDev
		self.srcDev = srcDev
		self.connId = connId
		self.isClient = isClient
		if isClient:
			assert srcDev == localDev
		else:
			assert dstDev == localDev			
		self.srcToDstSeqnr = 1
		self.dstToSrcSeqnr = 1
	
	def __getattr__(self, key):
		if key == "firstTime":
			if self.isClient:
				self.firstTime = self.clientFirstTime()
			else:
				self.firstTime = self.serverFirstTime()
			return self.firstTime
		if key == "connData":
			assert not self.isClient
			self.connData = self.readFileSrcToDst(self.initFn())
			return self.connData
		raise AttributeError, repr(self) + " has no attrib " + repr(key)
	
	def srcToDstPrefixFn(self):
		return self.dstDev.devId + "/messages-from-" + self.srcDev.devId + "/" + self.connId
	def dstToSrcPrefixFn(self):
		return self.dstDev.devId + "/messages-to-" + self.srcDev.devId + "/" + self.connId
	def readFileSrcToDst(self, fn):
		global localDev
		assert self.dstDev == localDev
		dstPrivKey = localDev.privateKeys.crypt
		srcPubKey = self.srcDev.publicKeys.sign
		return binstruct.readDecrypt(fs.open(fn), dstPrivKey, srcPubKey)
	def readFileDstToSrc(self, fn):
		global localDev
		assert self.srcDev == localDev
		srcPrivKey = localDev.privateKeys.crypt
		dstPubKey = self.dstDev.publicKeys.sign
		return binstruct.readDecrypt(fs.open(fn), srcPrivKey, dstPubKey)
	def writeFileDstToSrc(self, fn, v):
		global localDev
		assert self.dstDev == localDev
		try: fs.mkdir(fs.dirname(fn))
		except: pass # already existing. or so. we would fail anyway later
		srcPubKey = self.srcDev.publicKeys.crypt
		dstPrivKey = localDev.privateKeys.sign
		binstruct.writeEncrypt(fs.openW(fn), v, srcPubKey, dstPrivKey).close()
	def writeFileSrcToDst(self, fn, v):
		global localDev
		assert self.srcDev == localDev
		dstPubKey = self.dstDev.publicKeys.crypt
		srcPrivKey = localDev.privateKeys.sign
		binstruct.writeEncrypt(fs.openW(fn), v, dstPubKey, srcPrivKey).close()
	def verifyFile(self, fn, pubkey):
		binstruct.verifyFile(fs.open(fn), pubkey)
	def initFn(self):
		return self.srcToDstPrefixFn() + "-init"
	def ackFn(self):
		return self.srcToDstPrefixFn() + "-ack"		
	def refusedFn(self):
		return self.srcToDstPrefixFn() + "-refused"
	def clientFirstTime(self):
		assert self.srcDev == localDev
		fn = self.srcToDstPrefixFn() + "-clientFirstTime"
		return self.updateFirstTime(fn, self.srcDev.privateKeys.sign, self.srcDev.publicKeys.sign)
	def serverFirstTime(self):
		assert self.dstDev == localDev
		fn = self.srcToDstPrefixFn() + "-serverFirstTime"
		return self.updateFirstTime(fn, self.dstDev.privateKeys.sign, self.dstDev.publicKeys.sign)
	def updateFirstTime(self, fn, privSignKey, pubSignKey):
		try: v = binstruct.readDecrypt(fs.open(fn), verifysign_rsapubkey=pubSignKey)
		except IOError: v = None
		if v is None or time.time() < v:
			v = time.time()
			binstruct.writeEncrypt(fs.openW(fn), v, sign_rsaprivkey=privSignKey).close()
		return v

	def accept(self):
		if self.isClient: f = self.writeFileSrcToDst
		else: f = self.writeFileDstToSrc
		f(self.ackFn(), True)
	def refuse(self, reason):
		if self.isClient: f = self.writeFileSrcToDst
		else: f = self.writeFileDstToSrc
		f(self.refusedFn(), {"reason":reason})
	def isAwaiting(self):
		return not self.isAccepted() and not self.isRefused()
	def isAccepted(self):
		exAck = fs.exists(self.ackFn())
		if exAck: self.verifyFile(self.ackFn(), self.dstDev.publicKeys.sign)
		return exAck
	def isRefused(self):
		exRefused = fs.exists(self.refusedFn())
		if exRefused: self.verifyFile(self.refusedFn(), self.dstDev.publicKeys.sign)
		return exRefused		
	def close(self, reason=None):
		if self.isClient:
			self.writeFileSrcToDst(self.srcToDstPrefixFn() + "-close", {"reason":reason})
			return # cleanup will all be done by server
		for fn in fs.glob(self.dstDev.devId + "/messages-*-" + self.srcDev.devId + "/" + self.connId + "-*"):
			fs.remove(fn)
	def isOpen(self):
		if fs.exists(self.initFn()):
			self.verifyFile(self.initFn(), self.srcDev.publicKeys.sign)
			return True
		return False
	def hasCloseRequest(self):
		fn = self.srcToDstPrefixFn() + "-close"
		if fs.exists(fn):
			self.verifyFile(fn, self.srcDev.publicKeys.sign)
			return True
		return False
	
	def readPackages(self):
		if self.isClient: signPubKey = self.dstDev.publicKeys.sign
		else: signPubKey = self.srcDev.publicKeys.sign
		def incSeqNr():
			if self.isClient: self.dstToSrcSeqnr += 1
			else: self.srcToDstSeqnr += 1
		while True:
			if self.isClient:
				fn = self.dstToSrcPrefixFn() + "-" + str(self.dstToSrcSeqnr)
			else:
				fn = self.srcToDstPrefixFn() + "-" + str(self.srcToDstSeqnr)
			if not fs.exists(fn): break
			ackFn = fn + "-ack"
			if fs.exists(ackFn):
				incSeqNr()
				continue
			pkg = binstruct.Dict()
			if self.isClient:
				pkg.seqnr = self.dstToSrcSeqnr
				pkg.data = self.readFileDstToSrc(fn)
				self.writeFileSrcToDst(ackFn, True)
			else:
				pkg.seqnr = self.srcToDstSeqnr
				pkg.data = self.readFileSrcToDst(fn)
				self.writeFileDstToSrc(ackFn, pkg)
			yield pkg
			incSeqNr()

	def sendPackage(self, pkg):
		if self.isClient:
			fn = self.srcToDstPrefixFn() + "-" + str(self.srcToDstSeqnr)
			self.writeFileSrcToDst(fn, pkg)
			self.srcToDstSeqnr += 1
		else:
			fn = self.dstToSrcPrefixFn() + "-" + str(self.dstToSrcSeqnr)
			self.writeFileDstToSrc(fn, pkg)
			self.dstToSrcSeqnr += 1
		
def readPublicKeys(fn):
	keys = binstruct.read(fs.open(fn))
	assert isinstance(keys, dict)
	assert "crypt" in keys
	assert "sign" in keys
	return keys

def devices():
	devs = set()
	devdirs = fs.listdir(".")
	for devdir in devdirs:
		keysFn = devdir + "/publicKeys"
		if fs.isdir(devdir) and fs.exists(keysFn):
			devId = fs.basename(devdir)
			publicKeys = readPublicKeys(keysFn)
			d = Dev(devId, publicKeys)
			devs.add(d)
	for d in devs:
		yield d

def dev(publicKeys):
	return Dev(publicKeys)

def wait():
	# stupid for now...
	import sys, time
	try: time.sleep(2)
	except KeyboardInterrupt: sys.exit(1)
	# do pyinotify or so later...


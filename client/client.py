#!/usr/bin/python

# code by Albert Zeyer, www.az2000.de
# 2012-06-14

import os, os.path, sys
mydir = os.path.dirname(__file__) or os.getcwd()
mydir = os.path.abspath(mydir)
print "Hello from client."
print "mydir:", mydir
sys.path += [mydir + "/../common"]

import better_exchook
better_exchook.install()

import datetime, time
import re
import binstruct
from appinfo import *

localDev = binstruct.Dict()

print "easycfg setup ..."
import easycfg
easycfg.setup(userdir + "/client.cfg", globals(), ["localDev"])

if not localDev:
	pubCryptKey,privCryptKey = binstruct.genkeypair()
	pubSignKey,privSignKey = binstruct.genkeypair()
	localDev.publicKeys = binstruct.Dict({"crypt": pubCryptKey, "sign": pubSignKey})
	localDev.privateKeys = binstruct.Dict({"crypt": privCryptKey, "sign": privSignKey})
	easycfg.save()
localDev.type = "RemoteControlClient"
localDev.appInfo = {"appId":appid, "version":version}

print "fscomm setup ..."
import fscomm
fscomm.setup(appid, localDev)

print "register local dev ..."
localDev = fscomm.registerDev(localDev)

serverDev = None
for d in fscomm.devices():
	if d.type != "RemoteControlServer": continue
	print "found server:", d
	serverDev = d

def pushDataFile(fn):
	# TODO check change-time if needed...
	serverDev.storeData(localDev, fn, open(mydir + "/../pydata/" + fn).read())
	
def execRemotePy(conn, pythonCmd, wait=False):
	conn.sendPackage(pythonCmd)
	print "sent %r, waiting..." % pythonCmd

	while wait:
		for p in conn.readPackages():
			print "got", repr(p), "from", conn.dstDev
			return p
		try: time.sleep(0.5)
		except: sys.exit(1)
	
	if not wait:
		# just read and skip if there are any...
		for p in conn.readPackages(): pass

print "update media_keys.py ..."
pushDataFile("media_keys.py")

print "main connect ..."
execConn = serverDev.connectFrom(localDev, {"intent":"PythonExec.1"})

import atexit
atexit.register(lambda: execConn.close())

def doControl(ctrl):
	pyCmd = "eval(compile(" + \
		"dstDev.loadData(srcDev, 'media_keys.py') + " + \
		"'\\n\\nHIDPostAuxKey(NX_KEYTYPE_%s)'" % ctrl.upper() + \
		", '<>', 'exec'))"
	p = execRemotePy(execConn, pyCmd)
	if "ret" in p["data"]: return True
	else: return False
	
def main(arg):	
	if doControl(arg, wait=True): print "success!"
	else: print "failure"
	
if __name__ == '__main__':
	if hasattr(sys, "argv") and len(sys.argv) > 1:
		pythonCmd = sys.argv[1]
		main(pythonCmd)

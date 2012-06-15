#!/usr/bin/python

# code by Albert Zeyer, www.az2000.de
# 2012-06-14

import os, os.path, sys
mydir = os.path.dirname(__file__) or os.getcwd()
mydir = os.path.abspath(mydir)
sys.path += [mydir + "/../common"]

import better_exchook
better_exchook.install()

import datetime, time
import ast, subprocess
import re
import binstruct
from appinfo import *

localDev = binstruct.Dict()

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

import fscomm
fscomm.setup(appid, localDev)

localDev = fscomm.registerDev(localDev)

def main():
	serverDev = None
	for d in fscomm.devices():
		if d.type != "RemoteControlServer": continue
		print "found server:", d
		serverDev = d
	
	conn = serverDev.connectFrom(localDev, {"intent":"PythonExec.1"})
	conn.sendPackage("''.join(map(chr,range(97,100)))")
	print "sent, waiting..."
	while True:
		for p in conn.readPackages():
			print "got", repr(p), "from", c.dstDev
		try: time.sleep(10)
		except: sys.exit(1)
	
if __name__ == '__main__':
	main()
	
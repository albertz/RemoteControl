#!/usr/bin/python

# code by Albert Zeyer, www.az2000.de
# 2012-06-08

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

def local_filename_from_url(filename):
	if not filename.startswith("file://"): return None
	removestart = lambda s, t: s[len(t):] if s.startswith(t) else s
	filename = removestart(filename, "file://localhost")
	filename = removestart(filename, "file://")
	return filename

knownClientDevices = {}
localDev = binstruct.Dict()

import easycfg
easycfg.setup(userdir + "/server.cfg", globals(), ["knownClientDevices", "localDev"])

if not localDev:
	pubCryptKey,privCryptKey = binstruct.genkeypair()
	pubSignKey,privSignKey = binstruct.genkeypair()
	localDev.publicKeys = binstruct.Dict({"crypt": pubCryptKey, "sign": pubSignKey})
	localDev.privateKeys = binstruct.Dict({"crypt": privCryptKey, "sign": privSignKey})
	easycfg.save()
localDev.type = "RemoteControlServer"
localDev.appInfo = {"appId":appid, "version":version}

import fscomm
fscomm.setup(appid, localDev)

localDev = fscomm.registerDev(localDev)

import gui

def main():
	while True:

		for d in fscomm.devices():
			if d.type != "RemoteControlClient": continue
			if d.publicKeys.sign not in knownClientDevices:
				answer = gui.ask(
					"A new device was found:\n\n" +
					d.user_string() +
					"\nDo you want to allow full access on your computer?\n" +
					"(You can always disable the access again.)")
				devInfo = {}
				knownClientDevices[d.publicKeys.sign] = devInfo
				devInfo["devId"] = d.devId
				devInfo["publicKeys"] = d.publicKeys
				devInfo["allowAccess"] = answer

		for c in localDev.awaitingConnections():
			print "new conn:", c
			if c.srcDev.publicKeys.sign not in knownClientDevices:
				c.refuse("not accepted client " + c.srcDev.devId)
				continue
			if c.connData.intent == "PythonExec.1":
				c.accept()
			else:
				c.refuse("unknown intend '%s'" % c.intent)

		for c in localDev.connections():
			if c.hasCloseRequest():
				c.close()
				continue
			if time.time() - c.firstTime > 60: # old enough to cleanup
				c.close()
				continue
			if not c.isAccepted(): continue
			for p in c.readPackages():
				print "got", repr(p), "from", c.srcDev
				response = {}
				response["seqnr"] = p.seqnr
				try:
					ret = eval(p.data)
					response["ret"] = ret
				except Exception as exc:
					response["exception"] = repr(exc)
				c.sendPackage(response)

		easycfg.save()
		fscomm.wait()

if __name__ == "__main__":
	main()

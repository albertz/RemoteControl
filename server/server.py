#!/usr/bin/python

# code by Albert Zeyer, www.az2000.de
# 2012-06-08

import better_exchook
better_exchook.install()

import datetime, time
import os, os.path, sys
import ast, subprocess
import re
import binstruct

progname = "RemoteEverywhere"
appid = "com.albertzeyer." + progname
mydir = os.path.dirname(__file__) or os.getcwd()
userdir = "~/." + progname

def local_filename_from_url(filename):
	if not filename.startswith("file://"): return None
	removestart = lambda s, t: s[len(t):] if s.startswith(t) else s
	filename = removestart(filename, "file://localhost")
	filename = removestart(filename, "file://")
	return filename

if sys.platform == "darwin":
	userdir = "~/Library/Application Support/" + progname
elif sys.platform == "win32":
	from win32com.shell import shellcon, shell
	userdir = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0) + "/" + progname
	print >>sys.stderr, "WARNING: win32 support is untested"
else:
	raise Exception, "missing support for your platform"

userdir = os.path.expanduser(userdir)
try: os.makedirs(userdir)
except: pass

knownClientDevices = {}
localDev = binstruct.Dict()

import easycfg
easycfg.setup(userdir + "/server.cfg", globals(), ["knownClientDevices", "localDev"])

if not localDev:
	pubCryptKey,privCryptKey = binstruct.genkeypair()
	pubSignKey,privSignKey = binstruct.genkeypair()
	localDev.publicKeys = binstruct.Dict({"crypt": pubCryptKey, "sign": pubSignKey})
	localDev.privateKeys = binstruct.Dict({"crypt": privCryptKey, "sign": privSignKey})

import fscomm
fscomm.setup(appid, localDev)

import gui

def main():
	while True:

		for d in fscomm.devices():
			if d.type != "RemoteControlClient": continue
			if d.publicKey not in knownClientDevices:
				answer = gui.ask(
					"A new device was found:\n\n" +
					d.user_string() +
					"\nDo you want to allow full access on your computer?\n" +
					"(You can always disable the access again.)")
				devInfo = {}
				knownClientDevices[d.publicKey] = devInfo
				devInfo["devId"] = d.devId
				devInfo["publicKeys"] = d.publicKeys
				devInfo["allowAccess"] = answer

		for dInfo in knownClientDevices:
			d = fscomm.dev(dInfo.devId)
			for c in d.awaitingConnections():
				if c.intent == "PythonExec.1":
					c.accept()
				else:
					c.refuse("unknown intend '%s'" % c.intent)
			for c in d.connections():
				for p in c.readPackages():
					ret = eval(p.data)
					response = {}
					response["ret"] = ret
					response["seqnr"] = p.seqnr
					c.sendPackage(response)

		easycfg.save()
		fscomm.wait()

if __name__ == "__main__":
	main()

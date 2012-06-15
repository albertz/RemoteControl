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
	pass
	
if __name__ == '__main__':
	main()
	
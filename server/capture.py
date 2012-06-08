#!/usr/bin/python

import better_exchook
better_exchook.install()

import datetime, time
import os, os.path, sys
import ast, subprocess
import re

progname = "RemoteEverywhere"
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

def main():
	while True:
		#logfile = userdir + "/log-" + datetime.date.today().isoformat()
		#logfile = open(logfile, "a")
		#timetuple = datetime.datetime.today().timetuple()[0:6]
		#logfile.write( repr((timetuple, get_app_info())) + "\n" )
		#logfile.close()

		time.sleep(10)

if __name__ == "__main__":
	main()

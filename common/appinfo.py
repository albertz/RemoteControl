import sys, os

progname = "RemoteEverywhere"
appid = "com.albertzeyer." + progname
version = "1.0"

userdir = "~/." + progname

if sys.platform == "darwin":
	userdir = "~/Library/Application Support/" + progname
elif sys.platform == "win32":
	from win32com.shell import shellcon, shell
	userdir = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0) + "/" + progname
else:
	raise Exception, "missing support for your platform " + repr(sys.platform)

userdir = os.path.expanduser(userdir)
try: os.makedirs(userdir)
except: pass

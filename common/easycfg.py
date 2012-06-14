# easycfg
# code by Albert Zeyer, www.az2000.de
# 2012-06-08

CfgFile = None
cfg = {}

def setup(cfgfile, vars, varnames):
	global cfg, CfgFile
	CfgFile = cfgfile

	try:
		loadedCfg = eval(open(CfgFile).read())
		for vn in varnames:
			if vn in loadedCfg:
				vars[vn] = loadedCfg[vn]
	except IOError: # e.g. file-not-found. that's ok
		pass
	except:
		print "cfgfile reading error"
		sys.excepthook(*sys.exc_info())

	for vn in varnames:
		cfg[vn] = vars[vn]

def betterRepr(o):
	# the main difference: this one is deterministic
	# the orig dict.__repr__ has the order undefined.
	if isinstance(o, list):
		return "[" + ", ".join(map(betterRepr, o)) + "]"
	if isinstance(o, tuple):
		return "(" + ", ".join(map(betterRepr, o)) + ")"
	if isinstance(o, dict):
		return "{\n" + "".join(map(lambda (k,v): betterRepr(k) + ": " + betterRepr(v) + ",\n", sorted(o.iteritems()))) + "}"
	# fallback
	return repr(o)
	
def save():
	global cfg, CfgFile
	f = open(CfgFile, "w")
	f.write(betterRepr(cfg))
	f.write("\n")

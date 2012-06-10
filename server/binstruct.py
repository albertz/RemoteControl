# binstruct - binary structure serialization
# code by Albert Zeyer, 2012-06-10
# code under BSD

# I wanted sth as simple as Python repr or JSON, but:
#  - binary data should only add constant overhead
#  - very simple format
#  - very very big data should be possible
#  - searching through the file should be fast
# Where the first 2 points were so important for me that
# I implemented this format.

# Some related formats and the reasons they weren't good
# enough for me.
# BSON:
#  - keys in structs are only C-strings. I want
#    any possible data here.
#  - already too complicated
# Bencode:
#  - too restricted, too less formats
# OGDL:
#  - too simple
# ...

# ------- This format. ------------

# Integers. Use EliasGamma to decode the byte size
# of the signed integer. I.e. we start with EliasGamma,
# then align that to the next byte and the signed integer
# in big endian follows.

from array import array
from StringIO import StringIO

def bitsOf(n):
	assert n >= 0
	return n.bit_length()

def bitListToInt(l):
	i = 0
	bitM = 1
	for bit in reversed(l):
		i += bitM * int(bit)
		bitM <<= 1
	return i

def bitListToBin(l):
	bin = array("B", (0,)) * (len(l) / 8)
	for i in range(0, len(l), 8):
		byte = bitListToInt(l[i:i+8])
		bin[i/8] = byte
	return bin

def eliasGammaEncode(n):
	assert n > 0
	bitLen = bitsOf(n)
	binData = [False] * (bitLen - 1) # prefix
	bit = 2 ** (bitLen - 1)
	while bit > 0:
		binData += [bool(n & bit)]
		bit >>= 1
	binData += [False] * (-len(binData) % 8) # align by 8
	return bitListToBin(binData)

def eliasGammaDecode(stream):
	def readBits():
		while True:
			byte = ord(stream.read(1))
			bitM = 2 ** 7
			while bitM > 0:
				yield bool(byte & bitM)
				bitM >>= 1
	num = 0
	state = 0
	bitM = 1
	for b in readBits():
		if state == 0:
			if not b:
				bitM <<= 1
				continue
			state = 1
		num += bitM * int(b)
		bitM >>= 1
		if bitM == 0: break
	return num

def intToBin(x):
	bitLen = x.bit_length() if (x >= 0) else (x+1).bit_length() # two-complement
	bitLen += 1 # for the sign
	byteLen = (bitLen+7) / 8
	bin = array("B", (0,)) * byteLen
	if x < 0:
		x += 256 ** byteLen
		assert x > 0
	for i in range(byteLen):
		bin[byteLen-i-1] = (x >> (i * 8)) & 255
	return bin

def binToInt(bin):
	if isinstance(bin, str): bin = array("B", bin)
	n = 0
	byteLen = len(bin)
	for i in range(byteLen):
		n += bin[byteLen-i-1] << (i * 8)
	if n >= 2**(byteLen*8 - 1):
		n -= 256 ** byteLen
	return n

def intEncode(x):
	bin = intToBin(x)
	assert len(bin) > 0
	gammaBin = eliasGammaEncode(len(bin))
	return gammaBin + bin

def intDecode(stream):
	if isinstance(stream, array): stream = stream.tostring()
	if isinstance(stream, str): stream = StringIO(stream)
	binLen = eliasGammaDecode(stream)
	return binToInt(stream.read(binLen))
	
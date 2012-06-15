#!/usr/bin/python

import ctypes
dll = ctypes.CDLL("/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices")

#CGEventRef CGEventCreateKeyboardEvent (
#   CGEventSourceRef source,
#   CGKeyCode virtualKey,
#   bool keyDown
#);

# CGRemoteOperations.h
CGKeyCode = ctypes.c_uint16

# from CGEventTypes.h
CGEventRef = ctypes.POINTER(ctypes.c_int) # __CGEvent*
CGEventSourceRef = ctypes.POINTER(ctypes.c_int) # __CGEventSource*

# CGEvent.h
CGEventCreateKeyboardEvent = dll.CGEventCreateKeyboardEvent
CGEventCreateKeyboardEvent.argtypes = (CGEventSourceRef, CGKeyCode, ctypes.c_bool)
CGEventCreateKeyboardEvent.restype = CGEventRef

CGEventTapLocation = ctypes.c_uint32
CGEventPost = dll.CGEventPost
CGEventPost.argtypes = (CGEventTapLocation, CGEventRef)
CGEventPost.restype = None

CGEventType = ctypes.c_uint32
CGEventFlags = ctypes.c_uint64

CGEventSetType = dll.CGEventSetType
CGEventSetType.argtypes = (CGEventRef, CGEventType)
CGEventSetType.restype = None
CGEventSetFlags = dll.CGEventSetFlags
CGEventSetFlags.argtypes = (CGEventRef, CGEventFlags)
CGEventSetFlags.restype = None

CFRelease = dll.CFRelease
CFRelease.argtypes = (CGEventRef,)
CFRelease.restype = None

NSSystemDefined = 14 # NSEvent.h
NX_KEYTYPE_PLAY = 16

#ev = CGEventCreate()
#CGEventSetType(ev, NSSystemDefined)

#keyCode = NX_KEYTYPE_PLAY << 16
#keyDown = CGEventCreateKeyboardEvent(None, keyCode, True)
#keyUp = CGEventCreateKeyboardEvent(None, keyCode, False)

#CGEventSetFlags()

keyCode = NX_KEYTYPE_PLAY<<16 & 1
keyDown = CGEventCreateKeyboardEvent(None, keyCode, True)
#keyUp = CGEventCreateKeyboardEvent(None, keyCode, False)

CGEventPost(0, keyDown)

import time
for i in xrange(5): time.sleep(0.1)


#CGEventPost(0, keyUp)

#!/usr/bin/python

import ctypes
from ctypes import CDLL, c_int, c_bool, c_int16, c_uint16, c_uint32, c_int32, c_uint64, POINTER
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


# IOLLEvent.h
NX_KEYDOWN = 10
NX_KEYUP = 11
NX_SUBTYPE_AUX_CONTROL_BUTTONS = 8
NX_SYSDEFINED = 14
NSSystemDefined = 14 # NSEvent.h
kNXEventDataVersion = 2


NX_KEYTYPE_PLAY = 16
kern_return_t = ctypes.c_int

class NXEventDataCompoundMisc(ctypes.Union):
	_fields = [
		("F", ctypes.c_float * 11),
		("L", ctypes.c_int32 * 11),
		("S", ctypes.c_int16 * 22),
		("C", ctypes.c_int8 * 44)
	]
class NXEventDataCompound(ctypes.Structure):
	_fields_ = [
		("reserved", c_int16),
		("subType", c_int16),
		("misc", NXEventDataCompoundMisc),
		("__buffer", c_int32 * 16) # just to be sure
	]
class NXEventData(ctypes.Union):
	_fields_ = [
		("compound", NXEventDataCompound),
		# ...
	]
class NXEvent(ctypes.Structure):
	_fields_ = [
		("type", c_int32),
		("x", c_int32),
		("y", c_int32),
		("time", c_uint64),
		("flags", c_int32),
		("window", c_uint32),
		("service_id", c_uint64),
		("ext_pid", c_int32),
		("data", NXEventData)
	]

io_connect_t = POINTER(c_int) # actually IOObject* (device_types.h)
IOGPoint = c_uint64 # todo
IOOptionBits = c_uint64 # todo

# IOHIDLib.h
IOHIDPostEvent = dll.IOHIDPostEvent
IOHIDPostEvent.argtypes = (
	io_connect_t, c_uint32, IOGPoint,
	POINTER(NXEventData), c_uint32,
	IOOptionBits, IOOptionBits)
IOHIDPostEvent.restype = kern_return_t

def HIDPostAuxKey(auxKeyCode): # uint8
	event = NXEventData()
	kr = kern_return_t()
	loc = IOGPoint({ 0, 0 })

	# Key press event
	evtInfo = c_uint32(auxKeyCode << 16 | NX_KEYDOWN << 8)

	#  bzero(&event, sizeof(NXEventData));
	event.compound.subType = NX_SUBTYPE_AUX_CONTROL_BUTTONS;
	event.compound.misc.L[0] = evtInfo
	kr = IOHIDPostEvent(
		get_event_driver(), NX_SYSDEFINED, loc, event, kNXEventDataVersion, 0, False )
#  check( KERN_SUCCESS == kr );

# Key release event
#  evtInfo = auxKeyCode << 16 | NX_KEYUP << 8;
#  bzero(&event, sizeof(NXEventData));
#  event.compound.subType = NX_SUBTYPE_AUX_CONTROL_BUTTONS;
#  event.compound.misc.L[0] = evtInfo;
#  kr = IOHIDPostEvent( get_event_driver(), NX_SYSDEFINED, loc, &event, kNXEventDataVersion, 0, FALSE );
#  check( KERN_SUCCESS == kr );



#ev = CGEventCreate()
#CGEventSetType(ev, NSSystemDefined)

#keyCode = NX_KEYTYPE_PLAY << 16
#keyDown = CGEventCreateKeyboardEvent(None, keyCode, True)
#keyUp = CGEventCreateKeyboardEvent(None, keyCode, False)

#CGEventSetFlags()

#keyCode = NX_KEYTYPE_PLAY<<16 & 1
#keyDown = CGEventCreateKeyboardEvent(None, keyCode, True)
#keyUp = CGEventCreateKeyboardEvent(None, keyCode, False)

#CGEventPost(0, keyDown)

import Quartz
#import AppKit
ev = Quartz.NSEvent.otherEventWithType_location_modifierFlags_timestamp_windowNumber_context_subtype_data1_data2_(
	NSSystemDefined, # type
	(0,0), # location
	0xa00, # flags
	0, # timestamp
	0, # window
	0, # ctx
	8, # subtype
	(NX_KEYTYPE_PLAY << 16) | (0xa << 8), # data1
	-1 # data2
	)
cev = ev.CGEvent()
Quartz.CGEventPost(0, cev)
Quartz.CGEventPost(1, cev)
Quartz.CGEventPost(2, cev)

import time
for i in xrange(5): time.sleep(0.1)


#CGEventPost(0, keyUp)

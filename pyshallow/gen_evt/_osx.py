# OSX idle bypass script by (pussious) cfati

import ctypes as cts
import sys
from ctypes.util import find_library

CGFloat = cts.c_double if sys.maxsize > 0x100000000 else cts.c_float
UInt32 = cts.c_uint32
CGEventRef = cts.c_void_p
CGEventSourceRef = cts.c_void_p
CGEventTapLocation = UInt32

cgSessionEventTap = 1
mouseMoved = 5


class CGPoint(cts.Structure):
    _fields_ = (
        ("x", CGFloat),
        ("y", CGFloat),
    )


lib_path = find_library("CoreGraphics")
if not lib_path:
    print("Error loading Graphics lib")
    sys.exit(-1)
CoreGraphics = cts.CDLL(lib_path)

CGEventCreate = CoreGraphics.CGEventCreate
CGEventCreate.argtypes = (CGEventSourceRef,)
CGEventCreate.restype = CGEventRef

CGEventGetLocation = CoreGraphics.CGEventGetLocation
CGEventGetLocation.argtypes = (CGEventRef,)
CGEventGetLocation.restype = CGPoint

CFRelease = CoreGraphics.CFRelease
CFRelease.argtypes = (CGEventRef,)
CFRelease.restype = None

CGEventPost = CoreGraphics.CGEventPost
CGEventPost.argtypes = (CGEventTapLocation, CGEventSourceRef)
CGEventPost.restype = None

__warn = True


def simulate(verbose=False):
    global __warn
    if __warn:
        print(
            "-----"
            " If it doesn't work, the application running this script"
            " (e.g. Terminal) must be granted the 'Accessibility' permission"
            " -----"
        )
        __warn = False
    # evt = CGEventCreateMouseEvent(None, mouseMoved, CGPoint(-1, -1), -1)
    evt = CGEventCreate(None)
    if not evt:
        if verbose:
            print("Error setting cursor position.")
        return
    pt = CGEventGetLocation(evt)
    # ret = CGDisplayMoveCursorToPoint(CGMainDisplayID(), pt) == success
    # ret = CGWarpMouseCursorPosition(pt) == success
    if verbose:
        print("Mouse at ({:d}, {:d}).".format(round(pt.x), round(pt.y)))
    CGEventPost(cgSessionEventTap, evt)
    if verbose:
        print("Sent fake mouse move event.")
    CFRelease(evt)


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)

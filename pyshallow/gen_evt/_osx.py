# OSX idle bypass script by (pussious) cfati

import atexit
import ctypes as cts
import sys
from ctypes.util import find_library

CGFloat = cts.c_double if sys.maxsize > 0x100000000 else cts.c_float
UInt32 = cts.c_uint32
CGEventRef = cts.c_void_p
CGEventSourceRef = cts.c_void_p
CGEventTapLocation = UInt32

IOPMAssertionID = UInt32
IOPMAssertionIDPtr = cts.POINTER(IOPMAssertionID)
IOReturn = cts.c_uint32

cgSessionEventTap = 1
mouseMoved = 5

kCFStringEncodingUTF8 = 0x08000100

kIOPMAssertionLevelOn = 0xFF
kIOPMAssertionTypePreventUserIdleDisplaySleep = b"PreventUserIdleDisplaySleep"


class CGPoint(cts.Structure):
    _fields_ = (
        ("x", CGFloat),
        ("y", CGFloat),
    )


lib_path = find_library("ApplicationServices")
if not lib_path:
    print("Error loading ApplicationServices lib")
    sys.exit(-1)
ApplicationServices = cts.CDLL(lib_path)

lib_path = find_library("CoreGraphics")
if not lib_path:
    print("Error loading Graphics lib")
    sys.exit(-1)
CoreGraphics = cts.CDLL(lib_path)

lib_path = find_library("IOKit")
if not lib_path:
    print("Error loading IOKit lib")
    sys.exit(-1)
IOKit = cts.CDLL(lib_path)

AXIsProcessTrusted = ApplicationServices.AXIsProcessTrusted
AXIsProcessTrusted.argtypes = ()
AXIsProcessTrusted.restype = cts.c_bool

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

CFStringCreateWithCString = CoreGraphics.CFStringCreateWithCString
CFStringCreateWithCString.argtypes = (cts.c_void_p, cts.c_char_p, UInt32)
CFStringCreateWithCString.restype = cts.c_void_p

IOPMAssertionCreateWithName = IOKit.IOPMAssertionCreateWithName
IOPMAssertionCreateWithName.argtypes = (
    cts.c_void_p,
    UInt32,
    cts.c_void_p,
    IOPMAssertionIDPtr,
)
IOPMAssertionCreateWithName.restype = IOReturn

IOPMAssertionRelease = IOKit.IOPMAssertionRelease
IOPMAssertionRelease.argtypes = (IOPMAssertionID,)
IOPMAssertionRelease.restype = IOReturn

_ax_checked = False
_ax_trusted = False


def _check_accessibility():
    global _ax_checked, _ax_trusted
    if _ax_checked:
        return _ax_trusted
    _ax_trusted = AXIsProcessTrusted()
    if not _ax_trusted:
        assertion_type = CFStringCreateWithCString(
            None,
            kIOPMAssertionTypePreventUserIdleDisplaySleep,
            kCFStringEncodingUTF8,
        )
        assertion_name = CFStringCreateWithCString(
            None, b"pyshallow", kCFStringEncodingUTF8
        )
        assertion_id = IOPMAssertionID()
        res = IOPMAssertionCreateWithName(
            assertion_type,
            kIOPMAssertionLevelOn,
            assertion_name,
            cts.byref(assertion_id),
        )
        CFRelease(assertion_name)
        CFRelease(assertion_type)
        if res == 0:
            atexit.register(IOPMAssertionRelease, assertion_id.value)
        print(
            "\n-----"
            " The application running this script"
            " (e.g. Terminal) is not granted the 'Accessibility' permission,"
            " falling back to display sleep assertion (some features might not work)"
            " -----\n"
        )
    _ax_checked = True
    return _ax_trusted


def simulate(verbose=False):
    _check_accessibility()
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

# OSX idle bypass script by (pussious) cfati

from __future__ import annotations

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
CGEventPost.argtypes = (CGEventTapLocation, CGEventRef)
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
_assertion_id = None


def _acquire_assertion() -> None:
    global _assertion_id
    if _assertion_id is not None:
        return
    assertion_type = CFStringCreateWithCString(
        None,
        kIOPMAssertionTypePreventUserIdleDisplaySleep,
        kCFStringEncodingUTF8,
    )
    assertion_name = CFStringCreateWithCString(
        None, b"pyshallow", kCFStringEncodingUTF8
    )
    aid = IOPMAssertionID()
    res = IOPMAssertionCreateWithName(
        assertion_type,
        kIOPMAssertionLevelOn,
        assertion_name,
        cts.byref(aid),
    )
    CFRelease(assertion_name)
    CFRelease(assertion_type)
    if res == 0:
        _assertion_id = aid.value
        atexit.register(_release_assertion)


def _release_assertion() -> None:
    global _assertion_id
    if _assertion_id is not None:
        IOPMAssertionRelease(_assertion_id)
        _assertion_id = None


def cleanup() -> None:
    _release_assertion()


def _check_accessibility() -> bool:
    global _ax_checked, _ax_trusted
    if _ax_checked:
        if not _ax_trusted:
            _acquire_assertion()
        return _ax_trusted
    _ax_trusted = AXIsProcessTrusted()
    if not _ax_trusted:
        _acquire_assertion()
        if _assertion_id is not None:
            print(
                "\nThe application running this script"
                " (e.g. Terminal) is not granted the 'Accessibility' permission."
                " Falling back to display sleep assertion (some features might not work).\n"
            )
    _ax_checked = True
    return _ax_trusted


def simulate(verbose: bool = False) -> bool:
    _check_accessibility()
    # evt = CGEventCreateMouseEvent(None, mouseMoved, CGPoint(-1, -1), -1)
    evt = CGEventCreate(None)
    if not evt:
        if verbose:
            print("Error generating synthetic event.")
        return True
    pt = CGEventGetLocation(evt)
    # ret = CGDisplayMoveCursorToPoint(CGMainDisplayID(), pt) == success
    # ret = CGWarpMouseCursorPosition(pt) == success
    if verbose:
        print(f"Mouse at ({round(pt.x):d}, {round(pt.y):d}).")
    CGEventPost(cgSessionEventTap, evt)
    if verbose:
        print("Generated synthetic event.")
    CFRelease(evt)
    return True


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)

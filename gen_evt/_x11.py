# Nix (X11) idle bypass script by (pussious) cfati

import ctypes as cts
import os
import sys
from ctypes.util import find_library

"""
PointerWindow = 0

PointerMotionMask = 1 << 6
MotionNotify = 6
"""

IntPtr = cts.POINTER(cts.c_int)
UIntPtr = cts.POINTER(cts.c_uint)
DisplayPtr = cts.c_void_p
Bool = cts.c_int
XID = cts.c_ulong
Window = XID
WindowPtr = cts.POINTER(Window)

"""
CARD32 = XID
Time = CARD32
Status = cts.c_int


class XMotionEvent(cts.Structure):
    _fields_ = [
        ("type", cts.c_int),
        ("serial", cts.c_ulong),
        ("send_event", Bool),
        ("display", DisplayPtr),
        ("window", Window),
        ("root", Window),
        ("subwindow", Window),
        ("time", Time),
        ("x", cts.c_int),
        ("y", cts.c_int),
        ("x_root", cts.c_int),
        ("y_root", cts.c_int),
        ("state", cts.c_uint),
        ("is_hint", cts.c_char),
        ("same_screen", Bool),
    ]


class XEvent(cts.Union):
    _fields_ = [
        ("type", cts.c_int),
        ("xmotion", XMotionEvent),  # Many other fields exist
        ("pad", cts.c_long * 24),
    ]
"""

lib_path = find_library("X11")
if not lib_path:
    print("Error loading X lib")
    sys.exit(-1)
X11 = cts.CDLL(lib_path)

XOpenDisplay = X11.XOpenDisplay
XOpenDisplay.argtypes = (cts.c_char_p,)
XOpenDisplay.restype = DisplayPtr

XWarpPointer = X11.XWarpPointer
XWarpPointer.argtypes = (
    DisplayPtr,
    Window,
    Window,
    cts.c_int,
    cts.c_int,
    cts.c_uint,
    cts.c_uint,
    cts.c_int,
    cts.c_int,
)
XWarpPointer.restype = Bool

"""
XDefaultScreen = X11.XDefaultScreen
XDefaultScreen.argtypes = (DisplayPtr,)
XDefaultScreen.restype = cts.c_int
"""

XDefaultRootWindow = X11.XDefaultRootWindow
XDefaultRootWindow.argtypes = (DisplayPtr,)
XDefaultRootWindow.restype = Window

XQueryPointer = X11.XQueryPointer
XQueryPointer.argtypes = (
    DisplayPtr,
    Window,
    WindowPtr,
    WindowPtr,
    IntPtr,
    IntPtr,
    IntPtr,
    IntPtr,
    UIntPtr,
)
XQueryPointer.restype = Bool

"""
XSendEvent = X11.XSendEvent
XSendEvent.argtypes = (DisplayPtr, Window, Bool, cts.c_long, cts.POINTER(XEvent))
XSendEvent.restype = Status
"""

XFlush = X11.XFlush
XFlush.argtypes = (DisplayPtr,)
XFlush.restype = cts.c_int

XCloseDisplay = X11.XCloseDisplay
XCloseDisplay.argtypes = (DisplayPtr,)
XCloseDisplay.restype = None


__warn = bool(os.environ.get("DISPLAY", "").split(":")[0])


def _open_display(name=None, quit_on_error=False, verbose=False):
    # @TODO - cfati: Attempt a (timed) socket connection to the X Server?
    global __warn
    if __warn:
        print(
            "----- X Server custom config. There's a chance it might be unresponsive -----"
        )
        __warn = False
    disp_ptr = XOpenDisplay(name)
    if not disp_ptr:
        if verbose:
            print("Error contacting X Server")
        if quit_on_error:
            sys.exit(-1)
    return disp_ptr


pre_test = 0
if pre_test:
    # print("Probing for X Server...")
    _open_display(quit_on_error=True, verbose=True)


def simulate(verbose=False):
    display_ptr = _open_display(verbose=verbose)
    if not display_ptr:
        return
    # screen = XDefaultScreen(display_ptr)
    root_window = XDefaultRootWindow(display_ptr)
    root_wnd, child_wnd = Window(), Window()
    root_x, root_y = cts.c_int(0), cts.c_int(0)
    child_x, child_y = cts.c_int(0), cts.c_int(0)
    mask = cts.c_uint(0)

    """
    evt = XEvent()
    evt.type = MotionNotify
    evt.xmotion.send_event = 0
    evt.xmotion.same_screen = 1

    #print(evt.xmotion.root, evt.xmotion.subwindow)
    """

    res = XQueryPointer(
        display_ptr,
        root_window,
        cts.byref(root_wnd),
        cts.byref(child_wnd),
        cts.byref(root_x),
        cts.byref(root_y),
        cts.byref(child_x),
        cts.byref(child_y),
        cts.byref(mask),
    )
    if verbose:
        if res:
            print("Mouse at ({:d}, {:d}).".format(root_x.value, root_y.value))
        else:
            print("Error getting cursor position.")

    """
    print(res, mask)
    evt.xmotion.root = root_wnd
    evt.xmotion.subwindow = child_wnd
    evt.xmotion.x = child_x
    evt.xmotion.y = child_y
    evt.xmotion.root_x = root_x
    evt.xmotion.root_y = root_y
    evt.xmotion.state = 0 #mask

    res = XSendEvent(display_ptr, PointerWindow, 0, PointerMotionMask, cts.byref(evt))
    """

    res = XWarpPointer(display_ptr, 0, 0, 0, 0, 0, 0, 0, 0)
    if verbose:
        if res:
            print("Sent fake mouse move event.")
        else:
            print("Error setting cursor position.")

    XFlush(display_ptr)
    XCloseDisplay(display_ptr)


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)

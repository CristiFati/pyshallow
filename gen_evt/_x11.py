# Nix (X11) idle bypass script by (pussious) cfati

import ctypes as cts
import os
import sys
from ctypes.util import find_library

IntPtr = cts.POINTER(cts.c_int)
UIntPtr = cts.POINTER(cts.c_uint)
DisplayPtr = cts.c_void_p
Bool = cts.c_int
XID = cts.c_ulong
Window = XID
WindowPtr = cts.POINTER(Window)

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

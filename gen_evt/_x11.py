# Nix (X11) idle bypass script by (pussious) cfati

import ctypes as cts
import os
import socket
import sys
from ctypes.util import find_library

try:
    import pycfutils.network as pcun
except ImportError:
    # @TODO - cfati: Dev repository
    import pycfutils.pycfutils.network as pcun


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

_x_quick_check = True


def _is_x_server_listening():
    fails = (ConnectionRefusedError, socket.timeout)
    hds = os.environ.get("DISPLAY", "").split(":")
    host = "localhost"
    port = 6000
    if hds[0]:
        host = hds[0]
    if len(hds) == 2:
        d = hds[1].split(".")
        if d[0].isnumeric():
            port += int(d[0])
    try:
        pcun.connect_to_server(host, port, pcun.SOCKET_FAMILY_IPV4, attempt_timeout=0.5)
    except Exception as e:
        if isinstance(getattr(e, "__cause__"), fails):
            return False
    return True


def _open_display(name=None, quit_on_error=False, verbose=False):
    global _x_quick_check
    if _x_quick_check:
        if not _is_x_server_listening():
            if (
                input(
                    "A quick test shows that no XServer is listening."
                    " Press Y/y to continue anyway (in a possibly unresponsive manner): "
                ).lower()
                != "y"
            ):
                print("Aborted by user.")
                sys.exit(-1)
        _x_quick_check = False
    disp_ptr = XOpenDisplay(name)
    if not disp_ptr:
        if verbose:
            print("Error contacting XServer.")
        if quit_on_error:
            sys.exit(-1)
    return disp_ptr


def simulate(verbose=False):
    display_ptr = _open_display(verbose=verbose)
    if not display_ptr:
        return
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

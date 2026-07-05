# Nix (X11) idle bypass script by (pussious) cfati

from __future__ import annotations

import ctypes as cts
import os
import socket
import sys
from ctypes.util import find_library

import pycfutils.network as pcun

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
_exit_on_error = False


def _is_x_server_listening() -> bool:
    hds = os.environ.get("DISPLAY", "").split(":")
    host = hds[0]
    display = 0
    timeout = 0.5
    if len(hds) == 2:
        d = hds[1].split(".")
        if d[0].isnumeric():
            display = int(d[0])
    if host:
        try:
            pcun.connect_to_server(
                host, 6000 + display, pcun.SOCKET_FAMILY_IPV4, attempt_timeout=timeout
            )
        except Exception:
            return False
        return True
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect(f"/tmp/.X11-unix/X{display}")
    except OSError:
        return False
    finally:
        sock.close()
    return True


def _open_display(name: str | None = None) -> cts.c_void_p | None:
    global _x_quick_check
    if _x_quick_check:
        if not _is_x_server_listening():
            if (
                input(
                    "\nA quick test shows that no XServer is listening."
                    " Press Y/y to continue anyway (in a possibly unresponsive manner): "
                ).lower()
                != "y"
            ):
                print("Aborted by user.")
                return None
        _x_quick_check = False
    disp_ptr = XOpenDisplay(name)
    if not disp_ptr:
        print("Error contacting XServer.")
        disp_ptr = cts.c_void_p(0)
    return disp_ptr


def cleanup() -> None:
    pass


def simulate(verbose: bool = False) -> bool:
    global _exit_on_error
    display_ptr = _open_display()
    if display_ptr is None:
        return False
    elif not display_ptr:
        return not _exit_on_error
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
            print(f"Mouse at ({root_x.value:d}, {root_y.value:d}).")
        else:
            print("Error getting cursor position.")

    res = XWarpPointer(display_ptr, 0, 0, 0, 0, 0, 0, 0, 0)
    if verbose:
        if res:
            print("Generated synthetic event.")
        else:
            print("Error generating synthetic event.")

    XFlush(display_ptr)
    XCloseDisplay(display_ptr)
    return True


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)

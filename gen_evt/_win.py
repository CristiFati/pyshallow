# Win idle bypass script by (pussious) cfati

import ctypes as cts
import sys
from ctypes import wintypes as wts

MOUSEEVENTF_MOVE = 0x0001
INPUT_MOUSE = 0x0000


class MOUSEINPUT(cts.Structure):
    _fields_ = (
        ("dx", wts.LONG),
        ("dy", wts.LONG),
        ("mouseData", wts.DWORD),
        ("dwFlags", wts.DWORD),
        ("time", wts.DWORD),
        ("dwExtraInfo", cts.POINTER(wts.ULONG)),
    )


class _INPUT(cts.Union):
    _fields_ = (
        ("mi", MOUSEINPUT),
        ("ki", cts.c_ubyte),  # Dummy field - don't give a phuck
        ("hi", cts.c_ubyte),  # Dummy field - don't give a phuck
    )


class INPUT(cts.Structure):
    _anonymous_ = "u"
    _fields_ = (
        ("type", wts.DWORD),
        ("u", _INPUT),
    )


kernel32 = cts.WinDLL("kernel32.dll")

GetLastError = kernel32.GetLastError
GetLastError.argtypes = ()
GetLastError.restype = wts.DWORD

user32 = cts.WinDLL("user32.dll")

GetCursorPos = user32.GetCursorPos
GetCursorPos.argtypes = (cts.POINTER(wts.POINT),)
GetCursorPos.restype = wts.BOOL

SendInput = user32.SendInput
SendInput.argtypes = (wts.UINT, cts.POINTER(INPUT), cts.c_int)
SendInput.restype = wts.UINT


def simulate(verbose=False):
    point = wts.POINT()
    res = GetCursorPos(cts.byref(point))
    if verbose:
        if res:
            print("Mouse at ({:d}, {:d}).".format(point.x, point.y))
        else:
            print("Error ({:d}) getting cursor position.".format(GetLastError()))
    _input = INPUT()
    _input.type = INPUT_MOUSE
    _input.mi.dx = 0
    _input.mi.dy = 0
    _input.mi.dwFlags = MOUSEEVENTF_MOVE
    event_count = 1
    res = SendInput(event_count, cts.pointer(_input), cts.sizeof(INPUT))
    if verbose:
        if res:
            print("Sent fake mouse move event.")
        else:
            print("Error ({:d}) setting cursor position.".format(GetLastError()))


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)

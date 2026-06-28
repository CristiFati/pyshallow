# -*- mode: python ; coding: utf-8 -*-

import os
import platform
import subprocess
import sys

from pyshallow.version import __version_info__

PLATFORM_LINUX = "linux"
PLATFORM_MACOS = "macos"
PLATFORM_WINDOWS = "windows"

_platforms = {
    ("linux",): PLATFORM_LINUX,
    ("darwin",): PLATFORM_MACOS,
    ("win32",): PLATFORM_WINDOWS,
}
_platform = None
for keys, value in _platforms.items():
    if sys.platform in keys:
        _platform = value
        break
if _platform is None:
    raise RuntimeError(f"Unsupported platform: {sys.platform}")

_bits = 64 if sys.maxsize > 0x100000000 else 32
_machine = platform.machine()

_architectures = {
    PLATFORM_LINUX: {
        ("x86_64", 64): "x86_64",
        ("x86_64", 32): "i686",
        ("i686", 32): "i686",
        ("aarch64", 64): "arm64",
        ("arm", 32): "arm32",
    },
    PLATFORM_MACOS: {
        ("arm64", 64): "arm64",
        ("x86_64", 64): "x86_64",
    },
    PLATFORM_WINDOWS: {
        ("AMD64", 64): "x64",
        ("AMD64", 32): "x86",
        ("x86", 32): "x86",
        ("ARM64", 64): "arm64",
        ("ARM64", 32): "arm32",
    },
}

_arch = None
if _platform == PLATFORM_MACOS:
    try:
        result = subprocess.run(
            ["file", sys.executable], capture_output=True, text=True
        )
        if "universal" in result.stdout:
            _arch = "universal2"
    except FileNotFoundError:
        pass
if _arch is None and _platform in _architectures:
    for (mach, bits), arch in _architectures[_platform].items():
        if _machine.startswith(mach) and _bits == bits:
            _arch = arch
            break
if _arch is None:
    raise RuntimeError(
        f"Unsupported architecture: {_machine} {_bits}bit on {_platform}"
    )

if sys.platform == "darwin":
    os.environ["MACOSX_DEPLOYMENT_TARGET"] = "10.9"

_version = (
    f"{__version_info__[0]:04d}.{__version_info__[1]:02d}.{__version_info__[2]:02d}"
)
_pyver = f"py{sys.version_info.major}{sys.version_info.minor}"
_name = f"PyShallow-{_version}-{_platform}-{_arch}-{_pyver}"
_icon_exts = {PLATFORM_LINUX: ".png", PLATFORM_MACOS: ".icns", PLATFORM_WINDOWS: ".ico"}
_icon = f"assets/{_platform}/pyshallow{_icon_exts[_platform]}"

block_cipher = None

a = Analysis(
    ["pyshallow/__main__.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        "pyshallow.gen_evt._osx",
        "pyshallow.gen_evt._win",
        "pyshallow.gen_evt._x11",
        "pyshallow.gen_evt._android",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=sys.platform != "win32",
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon,
)

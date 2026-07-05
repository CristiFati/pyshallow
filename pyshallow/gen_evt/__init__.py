# Idle bypass script by (pussious) cfati

import sys

plat = sys.platform.lower()
if plat[:3] == "win":
    from ._win import cleanup, simulate
else:
    if plat == "darwin":
        from ._osx import cleanup, simulate
    elif hasattr(sys, "getandroidapilevel"):
        from ._android import cleanup, simulate
    # elif :  # More conditions could come here
    else:
        from ._x11 import cleanup, simulate


__all__ = (
    "cleanup",
    "simulate",
)


if __name__ == "__main__":
    print("This module is not meant to be run directly.\n")
    sys.exit(-1)

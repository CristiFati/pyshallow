
# Idle bypass script by (pussious) cfati

import sys

plat = sys.platform.lower()
if plat[:3] == "win":
    from ._win import simulate
else:
    if plat == "darwin":
        from ._osx import simulate
    #elif :  # More conditions could come here
    else:
        from ._x11 import simulate


__all__ = (
    "simulate",
)


if __name__ == "__main__":
    print("This module is not meant to be run directly.\n")
    sys.exit(-1)


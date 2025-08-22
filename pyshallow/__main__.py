#!/usr/bin/env python

# Idle bypass script by (pussious) cfati

import sys

from pyshallow import main

print(
    "Python {:s} {:03d}bit on {:s}\n".format(
        " ".join(item.strip() for item in sys.version.split("\n")),
        64 if sys.maxsize > 0x100000000 else 32,
        sys.platform,
    )
)
rc = main(*sys.argv[1:])
print("\nDone.\n")
sys.exit(rc)

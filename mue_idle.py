#!/usr/bin/env python

# Idle bypass script by (pussious) cfati

import argparse
import os
import sys
import time

"""
cur_dir = os.path.abspath(os.path.dirname(__file__))
if cur_dir not in sys.path:
    sys.path.append(cur_dir)
"""
import gen_evt as ge
from pyutils.kbd import read_key


__version_info__ = (0, 1)
__version__ = ".".join(str(e) for e in __version_info__)


def parse_args(*argv):
    parser = argparse.ArgumentParser(description="Suppress screen saver / turn off")
    parser.add_argument("--interval", "-i", type=int, default=200,
                        help="interval (seconds) between 2 consecutive events generation")
    parser.add_argument("--key_interval", "-k", type=float, default=0.5,
                        help="time (max seconds) needed by the script to become responsive to user input")
    parser.add_argument("--verbose", "-v", action="store_true", help="verbose mode")

    args, unk = parser.parse_known_args()
    if unk:
        print("Warning: Ignoring unknown arguments: {:}".format(unk))

    return args.interval, args.key_interval, args.verbose


def main(*argv):
    run_interval, key_interval, verbose = parse_args()

    verbose_text_pat = "\n{:s}\nAttempting to (fakely) move the mouse every {:d} seconds.\n" \
                       "  At any point, press a key to interrupt..."

    while True:
        if verbose:
            print(verbose_text_pat.format(time.strftime("%Y%m%d%H%M%S", time.gmtime())[2:], run_interval))
        res = ge.simulate(verbose=verbose)
        if read_key(interval=run_interval, poll_interval=key_interval):
            if verbose:
                print("\nKey pressed. Exiting.")
            break


if __name__ == "__main__":
    print("Python {:s} {:03d}bit on {:s}\n".format(" ".join(item.strip() for item in sys.version.split("\n")),
                                                   64 if sys.maxsize > 0x100000000 else 32, sys.platform))
    rc = main(*sys.argv[1:])
    print("\nDone.\n")
    sys.exit(rc)


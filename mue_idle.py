#!/usr/bin/env python

# Idle bypass script by (pussious) cfati

import argparse
import os
import random
import sys

try:
    from pycfutils.miscellaneous import timestamp_string
except ImportError:
    _pcfu = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pycfutils")
    if _pcfu not in sys.path:
        sys.path.insert(0, _pcfu)
    del _pcfu
    from pycfutils.miscellaneous import timestamp_string

import gen_evt as ge
from pycfutils.io import read_key

__version_info__ = (0, 0, 0)
__version__ = ".".join(str(e) for e in __version_info__)


def parse_args(*argv):
    parser = argparse.ArgumentParser(description="Suppress screen saver / turn off")
    parser.add_argument(
        "--base_interval",
        "-i",
        default=180,
        type=int,
        help="interval (seconds) between 2 consecutive events generation",
    )
    parser.add_argument(
        "--key_interval",
        "-k",
        default=0.5,
        type=float,
        help="time (max seconds) needed by the script to become responsive to user input",
    )
    parser.add_argument(
        "--max_deviation_percent",
        "-p",
        default=10,
        type=int,
        help="max base interval deviation percent."
        " A constant interval might be an indicator for monitoring tools that something fishy is going on."
        " Adding some randomization so each interval is different."
        " Make sure that if an event is required to happen at a certain rate,"
        " base interval + max deviation fit into that",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="verbose mode")

    args, unk = parser.parse_known_args()
    if unk:
        print("Warning: Ignoring unknown arguments: {:}".format(unk))

    if args.max_deviation_percent < 0:
        parser.exit(status=-1, message="Percent must be non negative\n")
    if args.base_interval <= 0 or args.key_interval <= 0:
        parser.exit(status=-1, message="Intervals must be positive\n")

    return args, unk


def generate_interval(base, deviation_percent):
    max_dev = base * deviation_percent / 100
    dev = max_dev * 2 * random.random()
    return max(round(base - max_dev + dev), 1)


def main(*argv):
    args, _ = parse_args()

    verbose_text_pat = (
        "\n{:s}\nAttempting to (fakely) move the mouse in {:d} seconds.\n"
        "  At any point, press a key to interrupt..."
    )

    while True:
        interval = generate_interval(args.base_interval, args.max_deviation_percent)
        if args.verbose:
            print(verbose_text_pat.format(timestamp_string()[2:], interval))
        res = ge.simulate(verbose=args.verbose)
        if read_key(timeout=interval, poll_interval=args.key_interval):
            if args.verbose:
                print("\nKey pressed. Exiting.")
            break


if __name__ == "__main__":
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


# Android idle bypass script by (pussious) cfati

import ctypes as cts
import sys


def simulate(verbose=False):
    res = False
    if verbose:
        if res:
            print("Mouse at ({:d}, {:d}).".format(0, 0))
        else:
            print("Error ({:d}) getting cursor position.".format(0))

    if verbose:
        if res:
            print("Sent fake mouse move event.")
        else:
            print("Error ({:d}) setting cursor position.".format(0))


if __name__ == "__main__":
    print("This script is not meant to be run directly.\n")
    sys.exit(-1)


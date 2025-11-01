# Idle bypass script by (pussious) cfati

import argparse
import random
import time

from pycfutils.io import read_key
from pycfutils.miscellaneous import timestamp_string

import pyshallow.gen_evt as ge


def parse_args(*argv):
    default_trigger_interval = 180
    default_key_interval = 0.5
    default_deviation_percent = 10

    parser = argparse.ArgumentParser(
        description="Suppress screen saver / lock / turn off"
    )
    parser.add_argument(
        "--trigger_interval",
        "-i",
        default=default_trigger_interval,
        type=int,
        help="interval (seconds) between 2 consecutive events generation."
        f" Default: {default_trigger_interval} second(s)",
    )
    parser.add_argument(
        "--key_interval",
        "-k",
        default=default_key_interval,
        type=float,
        help="time (max seconds) needed by the script"
        " to become responsive to user input (keyboard)."
        f" Default: {default_key_interval:.2f} second(s)",
    )
    parser.add_argument(
        "--max_deviation_percent",
        "-p",
        default=default_deviation_percent,
        type=int,
        help="maximum base interval deviation percent."
        " A constant interval might be an indicator for monitoring tools"
        " that something fishy is going on. Adding some randomization,"
        " so each interval is different. Make sure that if an event is required to happen"
        " in a certain amount of time, base interval + maximum deviation fits into that:"
        " `trigger_interval * (1 + max_deviation_percent) <= event_occurrence_timeout`."
        f" Default: {default_deviation_percent} (%%)",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        help="program execution (run) timeout (stop once it elapses)."
        " Can be provided as a number of seconds (integer) or using the"
        " `[h:]m:s` format, hours (if given) having no restrictions (can be higher than 24)."
        " Default: never timeout (0)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="verbose mode")

    args, unk = parser.parse_known_args()
    if unk:
        print("Warning: Ignoring unknown arguments: {:}".format(unk))

    if args.max_deviation_percent < 0:
        parser.exit(status=-1, message="Percent must be non negative\n")
    if args.trigger_interval <= 0 or args.key_interval <= 0:
        parser.exit(status=-1, message="Intervals must be positive\n")
    if args.key_interval * 2 > args.trigger_interval:
        parser.exit(
            status=-1, message="Key interval can be at most half of trigger interval\n"
        )
    if args.timeout:
        if args.timeout.isdecimal():
            args.timeout = int(args.timeout)
        else:
            parts = tuple(e.strip() for e in args.timeout.split(":"))
            if not parts or len(parts) > 3 or not all(e.isdecimal() for e in parts):
                parser.exit(status=-1, message="Invalid h:m:s specification\n")
            parts = tuple(int(e) for e in parts)
            if parts[-1] > 59 or parts[-2] > 59:
                parser.exit(status=-1, message="Invalid minutes or seconds\n")
            args.timeout = parts[-1] + parts[-2] * 60
            if len(parts) == 3:
                args.timeout += parts[0] * 3600
    else:
        args.timeout = 0

    return args, unk


def generate_interval(base, deviation_percent):
    max_dev = base * deviation_percent / 100
    dev = max_dev * 2 * random.random()
    return max(round(base - max_dev + dev), 1)


def run(trigger_interval, key_interval, max_deviation_percent, timeout, verbose):
    verbose_text_pat = (
        "\n{:s}\nAttempting to (fakely) move the mouse in {:.0f} second(s).\n"
        "  At any point, press any key to interrupt..."
    )
    if timeout > 0 and verbose:
        print(f"\nWill run for {timeout} second(s)...")
    start_time = time.time()
    while True:
        interval = generate_interval(trigger_interval, max_deviation_percent)
        if timeout > 0:
            elapsed = time.time() - start_time
            remaining = timeout - elapsed
            if remaining <= 0:
                if verbose:
                    print(f"\nTimeout ({elapsed:.0f} second(s)) reached. Exiting.")
                break
            elif remaining < interval:
                if verbose:
                    print("\nAdjusting intervals to fit in remaining timeout")
                interval = remaining
                key_interval = min(key_interval, interval / 2)
        if verbose:
            print(
                verbose_text_pat.format(
                    timestamp_string(human_readable=False)[2:], interval
                )
            )
        ge.simulate(verbose=verbose)
        if read_key(timeout=interval, poll_interval=key_interval):
            if verbose:
                print("\nKey pressed. Exiting.")
            break


def main(*argv):
    args, _ = parse_args()
    run(
        args.trigger_interval,
        args.key_interval,
        args.max_deviation_percent,
        args.timeout,
        args.verbose,
    )

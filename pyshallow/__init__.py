# Idle bypass script by (pussious) cfati

from __future__ import annotations

import argparse
import random
import time
from collections.abc import Sequence

from pycfutils.io import read_key
from pycfutils.miscellaneous import timestamp_string

import pyshallow.gen_evt as ge


def _parse_timeout(value: str | None, parser: argparse.ArgumentParser) -> int:
    if not value:
        return 0
    if value.isdecimal():
        return int(value)
    parts = tuple(e.strip() for e in value.split(":"))
    if not parts or len(parts) > 3 or not all(e.isdecimal() for e in parts):
        parser.exit(status=-1, message="Invalid h:m:s specification\n")
    parts = tuple(int(e) for e in parts)
    if parts[-1] > 59 or parts[-2] > 59:
        parser.exit(status=-1, message="Invalid minutes or seconds\n")
    result = parts[-1] + parts[-2] * 60
    if len(parts) == 3:
        result += parts[0] * 3600
    return result


def parse_args(argv: Sequence[str] | None) -> tuple[argparse.Namespace, list[str]]:
    default_trigger_interval = 180
    default_key_interval = 0.5
    default_deviation_percent = 10

    parser = argparse.ArgumentParser(
        description="Suppress screen saver / lock / turn off"
    )
    parser.add_argument(
        "--cycle_count",
        "-c",
        default=0,
        type=int,
        help="number of run/wait cycles to perform."
        " Only applicable when both run_timeout and wait_timeout are positive."
        " Default: 0 (unlimited)",
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
        " `trigger_interval * (1 + max_deviation_percent / 100) <= event_occurrence_timeout`."
        f" Default: {default_deviation_percent} (%%)",
    )
    parser.add_argument(
        "--run_timeout",
        "-t",
        help="program execution (run) timeout (stop once it elapses)."
        " Can be provided as a number of seconds (integer) or using the"
        " `[h:]m:s` format, hours (if given) having no restrictions (can be higher than 24)."
        " Default: never timeout (0)",
    )
    parser.add_argument(
        "--trigger_interval",
        "-i",
        default=default_trigger_interval,
        type=int,
        help="interval (seconds) between 2 consecutive events generation."
        f" Default: {default_trigger_interval} second(s)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="verbose mode")
    parser.add_argument(
        "--wait_timeout",
        "-w",
        help="wait (idle) timeout between run cycles."
        " Only applicable when run_timeout is also given and positive."
        " Can be provided as a number of seconds (integer) or using the"
        " `[h:]m:s` format, hours (if given) having no restrictions (can be higher than 24)."
        " Default: no wait (0)",
    )

    args, unk = parser.parse_known_args(argv)
    if unk:
        print(f"Warning: Ignoring unknown arguments: {unk}")

    if args.max_deviation_percent < 0:
        parser.exit(status=-1, message="Percent must be non negative\n")
    if args.trigger_interval <= 0 or args.key_interval <= 0:
        parser.exit(status=-1, message="Intervals must be positive\n")
    if args.key_interval * 2 > args.trigger_interval:
        parser.exit(
            status=-1, message="Key interval can be at most half of trigger interval\n"
        )
    args.run_timeout = _parse_timeout(args.run_timeout, parser)
    args.wait_timeout = _parse_timeout(args.wait_timeout, parser)

    if args.run_timeout == 0 and args.wait_timeout > 0:
        print("Warning: Wait timeout specifies when run timeout is 0. Ignoring")
        args.wait_timeout = 0
    if (args.run_timeout == 0 or args.wait_timeout == 0) and args.cycle_count > 0:
        print(
            "Warning: Cycle count specified without both timeouts being positive. Ignoring"
        )
        args.cycle_count = 0
    return args, unk


def _generate_interval(base: int, deviation_percent: int) -> int:
    max_dev = base * deviation_percent / 100
    dev = max_dev * 2 * random.random()
    return max(round(base - max_dev + dev), 1)


def _run(
    trigger_interval: int,
    key_interval: float,
    max_deviation_percent: int,
    run_timeout: int,
    wait_timeout: int,
    verbose: bool,
) -> bool:
    verbose_text_pat = (
        "\n{:s}\nAttempting to generate a synthetic event in {:.0f} second(s).\n"
        "  At any point, press any key to interrupt..."
    )
    if run_timeout > 0 and wait_timeout == 0 and verbose:
        print(f"\nWill run for {run_timeout} second(s)...")
    start_time = time.time()
    while True:
        interval = _generate_interval(trigger_interval, max_deviation_percent)
        if run_timeout > 0:
            elapsed = time.time() - start_time
            remaining = run_timeout - elapsed
            if remaining <= 0:
                if wait_timeout == 0 and verbose:
                    print(f"\nTimeout ({elapsed:.0f} second(s)) reached. Exiting.")
                return False
            elif remaining < interval:
                if wait_timeout == 0 and verbose:
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
        if read_key(timeout=interval, poll_interval=key_interval) is not None:
            if verbose:
                print("\nKey pressed. Exiting.")
            return True


def run(args: argparse.Namespace) -> int:
    verbose_wait_text_pat = (
        "\n{:s}\nAttempting to wait for {:.0f} second(s).\n"
        "  At any point, press any key to interrupt..."
    )
    run_args = (
        args.trigger_interval,
        args.key_interval,
        args.max_deviation_percent,
        args.run_timeout,
        args.wait_timeout,
        args.verbose,
    )

    if args.run_timeout and args.wait_timeout:
        cycle = 0
        while True:
            cycle += 1
            if _run(*run_args):
                break
            if 0 < args.cycle_count <= cycle:
                if args.verbose:
                    print(f"\nCycle count ({args.cycle_count}) reached. Exiting.")
                break
            if args.verbose:
                print(
                    verbose_wait_text_pat.format(
                        timestamp_string(human_readable=False)[2:], args.wait_timeout
                    )
                )
            if (
                read_key(timeout=args.wait_timeout, poll_interval=args.key_interval)
                is not None
            ):
                if args.verbose:
                    print("\nKey pressed. Exiting.")
                break
    else:
        _run(*run_args)
    return 0


def main(*argv) -> int:
    args, _ = parse_args(argv or None)
    return run(args)

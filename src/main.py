import sys
import time
import logging
import argparse

from core import STimer, TimeFormat


def timer_continue(timer):
    if timer.up:
        if timer.duration is None:
            return True
        elif timer.elapsed() < timer.duration:
            return True
    else:
        if timer.remaining() > 0:
            return True
    return False


def output_timer(timer):
    if timer.up:
        while timer_continue(timer) is True:
            print("\r" + timer.elapsed(TimeFormat.CLOCK), end="")
    else:
        while timer_continue(timer) is True:
            print("\r" + timer.remaining(TimeFormat.CLOCK), end="")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("duration", nargs="?")
    parser.add_argument("-u", "--up", action="store_true")
    args = parser.parse_args()

    timer = STimer(args.duration, args.up)
    timer.start()

    try:
        print("Timer started:")
        output_timer(timer)
        print()
        print("Time's up! Control + C to exit.", end="")
        sys.stdout.flush()
        while True:
            print("\a", end="")
            sys.stdout.flush()
            time.sleep(0.5)
    except KeyboardInterrupt:
        print()

    sys.exit(0)

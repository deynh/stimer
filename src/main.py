import sys
import logging
import argparse

from core import STimer
from core import TimeFormat


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("duration")
    args = parser.parse_args()

    timer = STimer(args.duration)
    timer.start()

    try:
        print("Timer started:")
        while timer.remaining() > 0:
            print("\r" + timer.remaining(TimeFormat.CLOCK), end="")

        print("\a\nControl + C to exit.")
        input()
    except KeyboardInterrupt:
        print()
        pass

    sys.exit(0)

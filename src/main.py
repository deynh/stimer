import sys
import time
import logging
import argparse

from core import STimer, TimeFormat
from confighandler import save_timer, load_timer, get_timers_list


def timer_continue(timer):
    if timer.up:
        if timer.duration() is None:
            return True
        elif timer.elapsed() < timer.duration():
            return True
    else:
        if timer.remaining() > 0:
            return True
    return False


def output_timer(timer):
    try:
        print("Timer started:")
        if timer.up:
            while timer_continue(timer) is True:
                print("\r" + timer.elapsed(TimeFormat.CLOCK), end="")
                sys.stdout.flush()
        else:
            while timer_continue(timer) is True:
                print("\r" + timer.remaining(TimeFormat.CLOCK), end="")
                sys.stdout.flush()
        print()
        print("Time's up! Control + C to exit.", end="")
        sys.stdout.flush()
        while True:
            print("\a", end="")
            sys.stdout.flush()
            time.sleep(0.5)
    except KeyboardInterrupt:
        print()


def list_timers():
    timers = get_timers_list()
    for timer in timers:
        name = timer[0]
        stimer = timer[1]
        timer_str = name + " " + stimer.duration(TimeFormat.CLOCK)
        if stimer.up:
            timer_str = timer_str + " UP"
        print(timer_str)


def parse(args):
    timer = None
    if args.timer:
        timer = load_timer(args.timer)
        if timer is None:
            print("Timer {} not found.".format(args.timer))
            sys.exit()
    elif args.list:
        list_timers()
        sys.exit(0)
    else:
        timer = STimer(args.duration, args.up)
    if args.save:
        if args.name:
            timer.name = args.name
        save_timer(timer)
    if args.save_only:
        if args.name:
            timer.name = args.name
        timer_name = save_timer(timer)
        print("Timer saved as timer " + timer_name)
        sys.exit(0)

    timer.start()
    output_timer(timer)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("duration", nargs="?")
    parser.add_argument("-u", "--up", action="store_true")
    save = parser.add_mutually_exclusive_group()
    save.add_argument("-s", "--save", action="store_true")
    save.add_argument("-S", "--save-only", action="store_true")
    save.add_argument("-t", "--timer")
    save.add_argument("-l", "--list", action="store_true")
    parser.add_argument("-n", "--name")
    args = parser.parse_args()
    parse(args)

    sys.exit(0)

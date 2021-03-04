import sys
import time
import logging
import argparse

from core import STimer, TimeFormat, parse_duration
from confighandler import save_timer, load_timer, get_timers_list, remove_timer

"""
    TODO:
        * No duplicate timer names
        * Output:
            - progress bar
            - elapsed time + remaining time
        * Help output
        * Better char_regex
            - 5h2m3m5s
        * --list filters
        * default settings
"""


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


def output_timer(timer, sound=True):
    try:
        print("Timer started:")
        if timer.up:
            while timer_continue(timer) is True:
                print(
                    "\r" + timer.elapsed(TimeFormat.CLOCK) + " \x08", end="", flush=True
                )
        else:
            while timer_continue(timer) is True:
                print(
                    "\r" + timer.remaining(TimeFormat.CLOCK) + " \x08",
                    end="",
                    flush=True,
                )
        print()
        if sound:
            print("Time's up! Control + C to exit.", end="", flush=True)
            while True:
                print("\a", end="", flush=True)
                time.sleep(0.5)
        else:
            print("Time's up!")
    except KeyboardInterrupt:
        print()


def list_timers():
    timers = get_timers_list()
    for timer in timers:
        name = timer[0]
        stimer = timer[1]
        duration = stimer.duration(TimeFormat.CLOCK)
        if duration is None:
            duration = "--"
        timer_str = name + " " + duration
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
    elif args.remove:
        removed = remove_timer(args.remove)
        if removed:
            print("Timer " + args.remove + " removed.")
        else:
            print("Timer " + args.remove + " not found.")
        sys.exit(0)
    else:
        duration = None
        if args.duration is None:
            if args.up is False:
                args.up = True
                print('No duration specified. Assuming "UP" (stopwatch) mode.')
        else:
            duration = parse_duration(args.duration)
            if duration is None:
                logging.error(
                    "Duration could not be parsed. Duration must be in character "
                    'format "#h#m#s.###" or clock format "##:##:##.###".'
                )
                sys.exit(0)
        timer = STimer(duration, args.up)
    if args.save or args.save_only:
        if args.name:
            timer.name = args.name
        timer_name = save_timer(timer)
        print("Timer saved as timer " + timer_name)
        if args.save_only:
            sys.exit(0)

    timer.start()
    output_timer(timer, not args.no_sound)


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
    save.add_argument("-r", "--remove")
    parser.add_argument("-n", "--name")
    parser.add_argument("-N", "--no-sound", action="store_true")
    args = parser.parse_args()
    parse(args)

    sys.exit(0)

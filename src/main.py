import sys
import logging
import argparse

from core import STimer, TimeFormat, parse_duration
from output import STimerOutput
from confighandler import (
    save_timer,
    load_timer,
    get_timers_list,
    remove_timer,
)

"""
    TODO:
        * Help output
        * Better char_regex
            - 5h2m3m5s
        * --list filters
        * Allow --timer and --save
"""


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


def set_timer_options(args, timer):
    args_options = {}
    if args.duration:
        duration = parse_duration(args.duration)
        if duration is None:
            logging.error(
                "Duration could not be parsed. Duration must be in character "
                'format "#h#m#s.###" or clock format "##:##:##.###".'
            )
            sys.exit(0)
        args_options["duration"] = duration
    if args.up:
        args_options["up"] = True
    elif args.down:
        args_options["up"] = False
    if args.name:
        args_options["name"] = args.name
    if args.sound:
        args_options["sound"] = True
    elif args.no_sound:
        args_options["sound"] = False
    if args.full:
        args_options["widget_fmt"] = "full"
    elif args.simple:
        args_options["simple"] = "simple"
    if args.precision is not None:
        args_options["precision"] = args.precision

    timer.option_dict = args_options

    if timer.duration() is None:
        if timer.up is None or timer.up is False:
            timer.up = True
            if args.down:
                print(
                    'Cannot run timer in "DOWN" (timer) mode with no duration. '
                    + 'Assuming "UP" (stopwatch) mode.'
                )
            else:
                print('No duration specified. Assuming "UP" (stopwatch) mode.')


def parse(args):
    timer = None
    if args.list:
        list_timers()
        sys.exit(0)
    elif args.remove:
        removed = remove_timer(args.remove)
        if removed:
            print("Timer " + args.remove + " removed.")
        else:
            print("Timer " + args.remove + " not found.")
        sys.exit(0)
    elif args.timer:
        timer = load_timer(args.timer)
        if timer is None:
            print("Timer {} not found.".format(args.timer))
            sys.exit(0)

    if timer is None:
        timer = STimer()
    set_timer_options(args, timer)

    if args.save or args.save_only:
        timer_name = save_timer(timer)
        if timer_name:
            print("Timer saved as: " + timer_name)
        else:
            sys.exit(0)
        if args.save_only:
            sys.exit(0)

    timer.start()
    timer_output = STimerOutput(timer)
    timer_output.start_output()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("duration", nargs="?")
    up = parser.add_mutually_exclusive_group()
    up.add_argument("-u", "--up", action="store_true")
    up.add_argument("-U", "--down", action="store_true")
    save = parser.add_mutually_exclusive_group()
    save.add_argument("-s", "--save", action="store_true")
    save.add_argument("-S", "--save-only", action="store_true")
    save.add_argument("-t", "--timer")
    save.add_argument("-l", "--list", action="store_true")
    save.add_argument("-r", "--remove")
    parser.add_argument("-n", "--name")
    sound = parser.add_mutually_exclusive_group()
    sound.add_argument("-a", "--no-sound", action="store_true")
    sound.add_argument("-A", "--sound", action="store_true")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("-o", "--simple", action="store_true")
    output.add_argument("-O", "--full", action="store_true")
    parser.add_argument("-p", "--precision", type=int)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig()

    parse(args)
    sys.exit(0)

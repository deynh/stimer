import sys
import time
import logging
import argparse

from core import STimer, TimeFormat, parse_duration
from output import STimerOutput
from confighandler import (
    save_timer,
    load_timer,
    get_timers_list,
    remove_timer,
    get_defaults,
)

"""
    TODO:
        * No duplicate timer names
        * Output:
            - decimal fraction
        * Help output
        * Better char_regex
            - 5h2m3m5s
        * --list filters
"""


def output_timer(timer):
    output_fmt = {}
    defaults = get_defaults()

    def widget_fmt(fmt):
        if fmt == "simple":
            output_fmt["progress_bar"] = False
            if timer.up:
                output_fmt["elapsed"] = True
                output_fmt["remaining"] = False
            else:
                output_fmt["elapsed"] = False
                output_fmt["remaining"] = True
        elif fmt == "full":
            output_fmt["progress_bar"] = True
            output_fmt["elapsed"] = True
            output_fmt["remaining"] = True

    if timer.up is not None:
        output_fmt["up"] = timer.up
    else:
        output_fmt["up"] = defaults["up"]
    if timer.sound is not None:
        output_fmt["sound"] = timer.sound
    else:
        output_fmt["sound"] = defaults["sound"]
    if timer.widget_fmt:
        widget_fmt(timer.widget_fmt)
    else:
        widget_fmt(defaults["widget_fmt"])

    timer_output = STimerOutput(timer, output_fmt)
    timer_output.start_output()


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
            sys.exit(0)
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

    duration = None
    up = None
    name = None
    sound = None
    widget_fmt = None
    if args.duration:
        duration = parse_duration(args.duration)
        if duration is None:
            logging.error(
                "Duration could not be parsed. Duration must be in character "
                'format "#h#m#s.###" or clock format "##:##:##.###".'
            )
            sys.exit(0)
    elif timer:
        duration = timer.duration()
    if args.up:
        up = True
    elif args.down:
        up = False
    elif timer:
        up = timer.up
    if duration is None:
        if up is None or up is False:
            up = True
            if args.down:
                print(
                    'Cannot run timer in "DOWN" mode with no duration. '
                    + 'Assuming "UP" (stopwatch) mode.'
                )
            else:
                print('No duration specified. Assuming "UP" (stopwatch) mode.')
    if args.name:
        name = args.name
    elif timer:
        name = timer.name
    if args.no_sound:
        sound = False
    elif args.sound:
        sound = True
    elif timer:
        sound = timer.sound
    if args.full:
        widget_fmt = "full"
    elif args.simple:
        widget_fmt = "simple"
    elif timer:
        widget_fmt = timer.widget_fmt
    timer = STimer(duration, up, name, sound, widget_fmt)

    if args.save or args.save_only:
        timer_name = save_timer(timer)
        print("Timer saved as timer " + timer_name)
        if args.save_only:
            sys.exit(0)

    timer.start()
    output_timer(timer)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

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
    args = parser.parse_args()
    parse(args)

    sys.exit(0)

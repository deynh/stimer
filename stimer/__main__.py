import sys
import logging
import argparse

from .core import STimer, TimeFormat, parse_duration
from .output import STimerOutput
from .confighandler import (
    save_timer,
    load_timer,
    get_timers_list,
    remove_timer,
)

VERSION = "v0.2.1"

HELP_MSGS = {
    "duration": (
        'Duration of timer in "hms" format or "clock" format.\n'
        "    hms format -> #h#m#s\n"
        "    clock format -> ##:##:##\n"
        'See "--help-duration"'
    ),
    "up": "count up (stopwatch mode), duration not required",
    "down": "count down (timer mode), default; useful to override saved timers",
    "no_sound": "no alert sound",
    "sound": "alert sound, default; useful to override saved timers",
    "simple": "simple output with no progress bar",
    "full": "full output, default; useful to override saved timers",
    "precision": "N {0, 1, 2...} decimal precision; default dependent on DURATION",
    "save": "save timer",
    "save_only": "save timer and do not run",
    "remove": "remove saved timer",
    "list": "list saved timers",
    "name": "name timer when saving",
    "timer": "run timer",
    "help_duration": (
        "Timer DURATION can be specified in 2 formats:\n"
        "\n"
        "hms format -> #h#m#s\n"
        "    where # can be any positive number including decimals.\n"
        '    "hms" refers to "hours", "minutes", and "seconds" respectively.\n'
        "    Any time unit can be omitted. "
        "Blanks between time units are counted as 0's.\n"
        "        Examples:\n"
        "            4h3s -> 4 hours and 3 seconds\n"
        "            1.5h -> 1 hour and 30 minutes\n"
        "            3h105.4m8s -> 4 hours 45 minutes and 32 seconds\n"
        "            3hm1s -> 3 hours and 1 second\n"
        "\n"
        "clock format -> ##:##:##\n"
        "    where # can be any positive number including decimals.\n"
        '    ":"\'s deliminate "hours", "minutes", and "seconds".\n'
        "    Leading time units can be omitted. "
        "Blanks between time units are counted as 0's.\n"
        "        Examples:\n"
        "            04:03 -> 4 minutes and 3 seconds\n"
        "            4:3 -> 4 minutes and 3 seconds\n"
        "            20 -> 20 seconds\n"
        "            5:00:6.5 -> 5 hours and 6.5 seconds\n"
        "            5::6.5 -> 5 hours and 6.5 seconds\n"
        "            5.5:: -> 5 hours and 30 minutes\n"
        "            :45: -> 45 minutes\n"
    ),
    "version": "output version information and exit",
}


def list_timers():
    timers = get_timers_list()
    rows = [("Name", "Duration", "Options")]
    column_len = [4, 8, 7]
    for timer in timers:
        name = timer[0]
        stimer = timer[1]
        options = stimer.option_dict
        row = [name]
        column_len[0] = max(len(row[0]), column_len[0])
        if stimer.duration():
            row.append(stimer.duration(TimeFormat.CLOCK))
        else:
            row.append("")
        column_len[1] = max(len(row[1]), column_len[1])
        options_entries = []
        if options["up"] is not None:
            if options["up"] is True:
                options_entries.append("up")
            else:
                options_entries.append("down")
        if options["sound"] is not None:
            if options["sound"] is True:
                options_entries.append("sound")
            else:
                options_entries.append("no sound")
        if options["widget_fmt"]:
            if options["widget_fmt"] == "simple":
                options_entries.append("simple")
            elif options["widget_fmt"] == "full":
                options_entries.append("full")
        if options["precision"] is not None:
            options_entries.append("precision " + str(options["precision"]))
        options_str = ", ".join(options_entries)
        row.append(options_str)
        column_len[2] = max(len(row[2]), column_len[2])
        rows.append(row)
    line_len = 0
    for i, row in enumerate(rows):
        row_str = "| "
        for j, entry in enumerate(row):
            if len(entry) < column_len[j]:
                entry = entry + " " * (column_len[j] - len(entry))
            row_str = row_str + entry + " | "
        row_str.strip()
        line_len = max(line_len, len(row_str))
        rows[i] = row_str
    rows.insert(1, "*" * line_len)
    for row in rows:
        print(row)


def set_timer_options(args, timer):
    args_options = {}
    if args.duration:
        duration = parse_duration(args.duration)
        if duration is None:
            print(
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
        args_options["widget_fmt"] = "simple"
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


def main():
    def help_formatter(prog):
        return argparse.RawTextHelpFormatter(prog, max_help_position=26)

    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTIONS]... DURATION",
        formatter_class=help_formatter,
    )
    parser.add_argument(
        "duration", nargs="?", help=HELP_MSGS["duration"], metavar="DURATION"
    )
    up = parser.add_mutually_exclusive_group()
    up.add_argument("-u", "--up", action="store_true", help=HELP_MSGS["up"])
    up.add_argument("-U", "--down", action="store_true", help=HELP_MSGS["down"])
    sound = parser.add_mutually_exclusive_group()
    sound.add_argument(
        "-a", "--no-sound", action="store_true", help=HELP_MSGS["no_sound"]
    )
    sound.add_argument("-A", "--sound", action="store_true", help=HELP_MSGS["sound"])
    output = parser.add_mutually_exclusive_group()
    output.add_argument("-o", "--simple", action="store_true", help=HELP_MSGS["simple"])
    output.add_argument("-O", "--full", action="store_true", help=HELP_MSGS["full"])
    parser.add_argument(
        "-p", "--precision", type=int, help=HELP_MSGS["precision"], metavar="N"
    )
    save = parser.add_mutually_exclusive_group()
    save.add_argument("-s", "--save", action="store_true", help=HELP_MSGS["save"])
    save.add_argument(
        "-S", "--save-only", action="store_true", help=HELP_MSGS["save_only"]
    )
    save.add_argument("-r", "--remove", help=HELP_MSGS["remove"], metavar="NAME")
    save.add_argument("-l", "--list", action="store_true", help=HELP_MSGS["list"])
    parser.add_argument("-n", "--name", help=HELP_MSGS["name"])
    parser.add_argument("-t", "--timer", help=HELP_MSGS["timer"], metavar="NAME")
    parser.add_argument("--version", action="store_true", help=HELP_MSGS["version"])
    parser.add_argument("--help-duration", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--debug", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig()
    if args.help_duration:
        print(HELP_MSGS["help_duration"])
        sys.exit(0)
    if args.version:
        print("stimer " + VERSION)
        sys.exit(0)

    try:
        parse(args)
    except KeyboardInterrupt:
        sys.exit(0)
    sys.exit(0)


if __name__ == "__main__":
    main()

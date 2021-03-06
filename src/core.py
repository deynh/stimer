import re
import sys
import json
import logging
import time
from enum import Enum


class TimeFormat(Enum):
    SECONDS = 0
    CLOCK = 1


class STimeData:
    def __init__(self, seconds):
        self._seconds = seconds

    def __call__(self, time_format=TimeFormat.SECONDS):
        if time_format is TimeFormat.CLOCK:
            return self.clock
        return self.seconds

    @property
    def seconds(self):
        return self._seconds

    @property
    def clock(self):
        minutes = self._seconds / 60
        hours_left = int(minutes / 60)
        mins_left = int((self._seconds / 60) - (60 * hours_left))
        secs_left = int(round(self._seconds % 60))
        if secs_left == 60:
            secs_left = 0
            mins_left = mins_left + 1
        if mins_left == 60:
            mins_left = 0
            hours_left = hours_left + 1
        clock_format = []
        clock_format.append(str(hours_left))
        clock_format.append(str(mins_left))
        clock_format.append(str(secs_left))
        clock_str = ""
        for s in clock_format:
            if len(s) < 2:
                s = "0" + s
            clock_str = clock_str + s + ":"
        clock_str = clock_str[:-1]
        return clock_str


def parse_duration(duration: str) -> float:
    def to_float(decimal_time: str) -> float:
        time = 0.0
        splits = decimal_time.split(".")
        if splits[0] != "":
            time = time + float(splits[0])
        if len(splits) > 1 and splits[1] != "":
            new_time = "0." + splits[1]
            time = time + float(new_time)
        return time

    if duration is None:
        return None

    char_regex = r"(?i)(?=^[\d\.hms]*[hms][\d\.hms]*$)([\d\.[hms]*[hms][\d\.hms]*){1,3}"
    clock_regex = r"^((?=((:)|(\d+)))(:?\d*\.?\d*){1,3})$"
    char_pattern = re.compile(char_regex)
    clock_pattern = re.compile(clock_regex)
    char_match = re.match(char_pattern, duration)
    clock_match = re.match(clock_pattern, duration)

    seconds = 0.0
    if char_match:
        logging.debug("Duration matched character format.")
        hours_pattern = re.compile(r"(?i)\d*\.?\d*[h]")
        mins_pattern = re.compile(r"(?i)\d*\.?\d*[m]")
        secs_pattern = re.compile(r"(?i)\d*\.?\d*[s]?$")
        hours_match = re.search(hours_pattern, duration)
        mins_match = re.search(mins_pattern, duration)
        secs_match = re.search(secs_pattern, duration)

        if hours_match:
            hours = hours_match[0][:-1]
            hours = to_float(hours)
            seconds = seconds + (hours * 60 * 60)
        if mins_match:
            mins = mins_match[0][:-1]
            mins = to_float(mins)
            seconds = seconds + (mins * 60)
        if secs_match:
            secs = secs_match[0]
            if len(secs) > 0 and secs[-1] == "s":
                secs = secs[:-1]
            secs = to_float(secs)
            seconds = seconds + secs
    elif clock_match:
        logging.debug("Duration matched clock format.")
        duration_splits = duration.split(":")
        duration_splits.reverse()
        multiplier = 1
        for split in duration_splits:
            split = to_float(split)
            seconds = seconds + (multiplier * split)
            multiplier = multiplier * 60
    else:
        logging.debug("Duration did not match pattern.")
        return None
    return seconds


class STimer:
    def __init__(self, **kwargs):
        self._duration = None
        self.up = None
        self.name = None
        self.sound = None
        self.widget_fmt = None
        self._start_time = None
        self.option_dict = kwargs

    @classmethod
    def from_json(cls, json_str):
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logging.error("JSON timer could not be decoded: " + e)
            return None
        return cls(**data)

    @property
    def option_dict(self):
        options = {
            "duration": self.duration(),
            "up": self.up,
            "name": self.name,
            "sound": self.sound,
            "widget_fmt": self.widget_fmt,
        }
        return options

    @option_dict.setter
    def option_dict(self, options):
        for option in options:
            if option == "duration":
                self._duration = options[option]
            elif option == "up":
                self.up = options[option]
            elif option == "name":
                self.name = options[option]
            elif option == "sound":
                self.sound = options[option]
            elif option == "widget_fmt":
                self.widget_fmt = options[option]
            else:
                logging.warning("Invalid key passed to STimer().option_dict")

    def to_json(self):
        data = {
            "duration": self.duration(),
            "up": self.up,
            "name": self.name,
            "sound": self.sound,
            "widget_fmt": self.widget_fmt,
        }
        return json.dumps(data)

    def duration(self, time_format=TimeFormat.SECONDS):
        if self._duration is None:
            return None
        stime = STimeData(self._duration)
        return stime(time_format)

    def elapsed(self, time_format=TimeFormat.SECONDS):
        elapsed_time = None
        if self._start_time is None:
            elapsed_time = 0.0
        else:
            elapsed_time = time.time() - self._start_time
            if self.duration():
                elapsed_time = min(elapsed_time, self.duration())
        stime = STimeData(elapsed_time)
        return stime(time_format)

    def remaining(self, time_format=TimeFormat.SECONDS):
        if self.duration() is None:
            return None
        secs_remaining = self.duration() - self.elapsed()
        stime = STimeData(secs_remaining)
        return stime(time_format)

    def start(self):
        self._start_time = time.time()
        if self.duration() is None:
            if self.up is None or self.up is False:
                logging.critical(
                    'STimer started in "DOWN" (timer) mode with no duration specified.'
                )
                sys.exit(1)
        logging.debug(
            "STimer started with duration: " + (str(self.duration()) or "None")
        )

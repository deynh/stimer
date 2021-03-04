import re
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
    def to_float(decimel_time: str) -> float:
        time = 0.0
        splits = decimel_time.split(".")
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
    def __init__(self, duration: float = None, up: bool = False, name: str = None):
        self._duration = duration
        self.up = up
        self.name = name
        self._start_time = None

    @classmethod
    def from_json(cls, json_str):
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            logging.error("JSON timer could not be decoded: " + e)
            return None
        duration = None
        up = False
        name = None
        if "duration" in data:
            duration = data["duration"]
        if "up" in data:
            up = data["up"]
        if "name" in data:
            name = data["name"]
        return cls(duration, up, name)

    def to_json(self):
        data = {
            "name": self.name,
            "duration": self.duration(),
            "up": self.up,
        }
        return json.dumps(data)

    def duration(self, time_format=TimeFormat.SECONDS):
        if self._duration is None:
            return None
        stime = STimeData(self._duration)
        return stime(time_format)

    def elapsed(self, time_format=TimeFormat.SECONDS):
        if self._start_time is None:
            return None
        elapsed_time = time.time() - self._start_time
        stime = STimeData(elapsed_time)
        return stime(time_format)

    def remaining(self, time_format=TimeFormat.SECONDS):
        if self.duration() is None:
            return None
        secs_remaining = self.duration() - (self.elapsed() or 0)
        stime = STimeData(secs_remaining)
        return stime(time_format)

    def start(self):
        self._start_time = time.time()
        logging.debug(
            "Timer started with duration: " + (str(self.duration()) or "None")
        )

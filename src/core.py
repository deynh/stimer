import re
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
        secs_left = int(round(self._seconds % 60))
        hours = minutes / 60
        mins_left = int(round(minutes % 60))
        hours_left = int(round(hours))
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


class STimer:
    def __init__(self, duration, up=False):
        self.duration = self.parse_duration(duration)
        self.up = up
        self._start_time = None

    def elapsed(self, time_format=TimeFormat.SECONDS):
        if self._start_time is None:
            return None
        elapsed_time = time.time() - self._start_time
        stime = STimeData(elapsed_time)
        return stime(time_format)

    def remaining(self, time_format=TimeFormat.SECONDS):
        if self.duration is None:
            return None
        secs_remaining = self.duration - (self.elapsed() or 0)
        stime = STimeData(secs_remaining)
        return stime(time_format)

    def start(self):
        self._start_time = time.time()

    def parse_duration(self, duration):
        # TODO: Match decimel fractions for character format
        if duration is None:
            return None
        char_regex = r"(?i)^(((?=\d+[hms])((\d*[hms])|(\d*[ms])|(\d*[s]))){1,3})$"
        clock_regex = r"^(((?=((:)|(\d+)))(:?\d*){1,3})|((?=((\d+)|(\.)))\d*\.\d*))$"
        char_pattern = re.compile(char_regex)
        clock_pattern = re.compile(clock_regex)
        char_match = re.match(char_pattern, duration)
        clock_match = re.match(clock_pattern, duration)

        seconds = 0.0
        if char_match:
            logging.debug("Duration matched character format.")
            hours_pattern = re.compile(r"(?i)\d+[h]")
            mins_pattern = re.compile(r"(?i)\d+[m]")
            secs_pattern = re.compile(r"(?i)\d+[s]")
            secs_only_pattern = re.compile(r"^\d+$")
            hours_match = re.search(hours_pattern, duration)
            mins_match = re.search(mins_pattern, duration)
            secs_match = re.search(secs_pattern, duration)
            secs_only_match = re.match(secs_only_pattern, duration)

            if secs_only_match:
                secs = secs_only_match[0]
                seconds = seconds + float(secs)
                return seconds
            if hours_match:
                hours = hours_match[0][:-1]
                seconds = seconds + (float(hours) * 60 * 60)
            if mins_match:
                mins = mins_match[0][:-1]
                seconds = seconds + (float(mins) * 60)
            if secs_match:
                secs = secs_match[0][:-1]
                seconds = seconds + float(secs)
        elif clock_match:
            logging.debug("Duration matched clock format.")
            duration_splits = duration.split(":")
            duration_splits.reverse()
            if "." in duration_splits[0]:
                secs_split = duration_splits[0].split(".")
                if secs_split[0]:
                    secs = secs_split[0]
                    seconds = seconds + float(secs)
                if secs_split[1]:
                    secs_fraction = secs_split[1]
                    secs_fraction = "0." + secs_fraction
                    seconds = seconds + float(secs_fraction)
            else:
                seconds = seconds + float(duration_splits[0])
            multiplier = 60
            if len(duration_splits) > 1:
                for split in duration_splits[1:]:
                    seconds = seconds + (multiplier * float(split))
                    multiplier = multiplier * 60
        else:
            logging.debug("Duration did not match pattern.")
            return None
        return seconds

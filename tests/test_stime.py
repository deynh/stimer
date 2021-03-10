import unittest

from stimer.core import STimeData, STimer, parse_duration


class TestSTimeDataClock(unittest.TestCase):
    def test_clock_seconds(self):
        stime_data = STimeData(24)
        clock_fmt = stime_data.clock()
        self.assertEqual(clock_fmt, "00:00:24")

    def test_clock_minutes(self):
        stime_data = STimeData(78)
        clock_fmt = stime_data.clock()
        self.assertEqual(clock_fmt, "00:01:18")

    def test_clock_hours(self):
        stime_data = STimeData(5621)
        clock_fmt = stime_data.clock()
        self.assertEqual(clock_fmt, "01:33:41")

    def test_clock_frac_secs(self):
        stime_data = STimeData(34.125)
        clock_fmt = stime_data.clock(3)
        self.assertEqual(clock_fmt, "00:00:34.125")

    def test_clock_frac_mins(self):
        stime_data = STimeData(82.133)
        clock_fmt = stime_data.clock(3)
        self.assertEqual(clock_fmt, "00:01:22.133")

    def test_clock_frac_hours(self):
        stime_data = STimeData(4599.55)
        clock_fmt = stime_data.clock(2)
        self.assertEqual(clock_fmt, "01:16:39.55")

    def test_clock_prec_secs(self):
        stime_data = STimeData(54)
        clock_fmt = stime_data.clock(4)
        self.assertEqual(clock_fmt, "00:00:54.0000")

    def test_clock_prec_mins(self):
        stime_data = STimeData(541)
        clock_fmt = stime_data.clock(2)
        self.assertEqual(clock_fmt, "00:09:01.00")

    def test_clock_prec_hours(self):
        stime_data = STimeData(16779)
        clock_fmt = stime_data.clock(5)
        self.assertEqual(clock_fmt, "04:39:39.00000")

    def test_clock_prec_frac_secs(self):
        stime_data = STimeData(22.554)
        clock_fmt = stime_data.clock(1)
        self.assertEqual(clock_fmt, "00:00:22.6")

    def test_clock_prec_frac_mins(self):
        stime_data = STimeData(905.1)
        clock_fmt = stime_data.clock(4)
        self.assertEqual(clock_fmt, "00:15:05.1000")

    def test_clock_prec_frac_hours(self):
        stime_data = STimeData(7880.16561)
        clock_fmt = stime_data.clock(3)
        self.assertEqual(clock_fmt, "02:11:20.166")


class TestParseDuration(unittest.TestCase):
    def test_char_secs(self):
        self.assertEqual(parse_duration("124s"), 124.0)

    def test_char_mins(self):
        self.assertEqual(parse_duration("5m"), 300.0)

    def test_char_hours(self):
        self.assertEqual(parse_duration("6h"), 21600.0)

    def test_char_ms(self):
        self.assertEqual(parse_duration("4m12s"), 252.0)

    def test_char_ms_plus(self):
        self.assertEqual(parse_duration("4m600s"), 840.0)

    def test_char_hms(self):
        self.assertEqual(parse_duration("6h1m12s"), 21672.0)

    def test_char_hs_plus(self):
        self.assertEqual(parse_duration("7h124s"), 25324.0)

    def test_char_frac_hours(self):
        self.assertEqual(parse_duration("4.5h"), 16200.0)

    def test_char_frac_hm_plus(self):
        self.assertEqual(parse_duration("4.5h120.6m"), 23436.0)

    def test_char_frac_hms_plus(self):
        self.assertEqual(parse_duration("66h400.125m5.6s"), 261613.1)

    def test_clock_secs(self):
        self.assertEqual(parse_duration("00:00:50"), 50.0)

    def test_clock_secs_only(self):
        self.assertEqual(parse_duration("54"), 54.0)

    def test_clock_secs_only_plus(self):
        self.assertEqual(parse_duration("124"), 124.0)

    def test_clock_secs_zeros(self):
        self.assertEqual(parse_duration("00:39"), 39.0)

    def test_clock_hms_blanks(self):
        self.assertEqual(parse_duration("::46"), 46.0)

    def test_clock_secs_blanks_zeros(self):
        self.assertEqual(parse_duration("00::3"), 3.0)

    def test_clock_mins_blanks(self):
        self.assertEqual(parse_duration("600:"), 36000.0)

    def test_clock_frac_hours_blanks(self):
        self.assertEqual(parse_duration("45.122::"), 162439.2)

    def test_clock_frac_hms(self):
        self.assertEqual(parse_duration("5.1:22.110:400.5"), 20087.1)

    def test_invalid_char(self):
        self.assertIsNone(parse_duration("4a"))

    def test_invalid_char_append_hms(self):
        self.assertIsNone(parse_duration("5h1m22s7t"))

    def test_invalid_char_hms(self):
        self.assertIsNone(parse_duration("ahbmcs"))

    def test_invalid_clock_extra(self):
        self.assertIsNone(parse_duration("5:1:124:6"))

    def test_invalid_clock_hours_extra_blanks(self):
        self.assertIsNone(parse_duration("1:::"))

    def test_invalid_clock_nondigit_mins(self):
        self.assertIsNone(parse_duration("a:"))

    def test_invalid_clock_nondigit_hms(self):
        self.assertIsNone(parse_duration("a:b:c"))


class TestSTimer(unittest.TestCase):
    def test_precision_whole(self):
        stimer = STimer(duration=12)
        self.assertEqual(stimer.precision, 0)

    def test_precision_one(self):
        stimer = STimer(duration=15.4)
        self.assertEqual(stimer.precision, 1)

    def test_precision_two(self):
        stimer = STimer(duration=120.45)
        self.assertEqual(stimer.precision, 2)

    def test_precision_override_greater(self):
        stimer = STimer(duration=12.5)
        options = {"precision": 3}
        stimer.option_dict = options
        self.assertEqual(stimer.precision, 3)

    def test_precision_override_lesser(self):
        stimer = STimer(duration=12.5)
        options = {"precision": 0}
        stimer.option_dict = options
        self.assertEqual(stimer.precision, 0)


if __name__ == "__main__":
    unittest.main()

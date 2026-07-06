"""Unit tests for --timestamps parsing + out-of-range handling (pure, no ffmpeg)."""
import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPT_DIR))

from frames import parse_timestamps, select_valid_times  # noqa: E402


class TestTimestampParse(unittest.TestCase):

    def test_mixed_formats(self):
        # 5 -> 5s, 1:30 -> 90s, 2:00 -> 120s
        self.assertEqual(parse_timestamps("5,1:30,2:00"), [5.0, 90.0, 120.0])

    def test_hms_and_whitespace(self):
        self.assertEqual(parse_timestamps(" 1:00:00 , 90 "), [3600.0, 90.0])

    def test_empty_and_none(self):
        self.assertEqual(parse_timestamps(""), [])
        self.assertEqual(parse_timestamps(None), [])
        self.assertEqual(parse_timestamps("5,,10"), [5.0, 10.0])


class TestSelectValidTimes(unittest.TestCase):

    def test_sorts_ascending(self):
        self.assertEqual(
            select_valid_times([30.0, 5.0, 15.0], duration=60.0),
            [5.0, 15.0, 30.0],
        )

    def test_drops_out_of_range(self):
        # duration 36s: 90 and 120 past the end are dropped, 5 kept.
        self.assertEqual(
            select_valid_times([5.0, 90.0, 120.0], duration=36.0),
            [5.0],
        )

    def test_drops_negative(self):
        self.assertEqual(select_valid_times([-1.0, 10.0], duration=60.0), [10.0])

    def test_unknown_duration_keeps_all(self):
        # duration 0 (unknown) -> no upper-bound filtering, still sorted.
        self.assertEqual(
            select_valid_times([9999.0, 5.0], duration=0.0),
            [5.0, 9999.0],
        )


if __name__ == "__main__":
    unittest.main()

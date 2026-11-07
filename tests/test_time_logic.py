"""Unit tests for the countdown math (calendar months, rollover, DST-free)."""
import os
import sys
import unittest
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from time_logic import (  # noqa: E402
    add_months,
    is_challenge_active,
    next_target,
    remaining,
    timezone_name,
)


class TestAddMonths(unittest.TestCase):
    def test_simple_shift(self):
        self.assertEqual(
            add_months(datetime(2026, 8, 20, 10, 0), 2),
            datetime(2026, 10, 20, 10, 0),
        )

    def test_year_wrap(self):
        self.assertEqual(
            add_months(datetime(2026, 11, 15), 3), datetime(2027, 2, 15)
        )

    def test_day_clamps_to_short_month(self):
        self.assertEqual(
            add_months(datetime(2026, 1, 31), 1), datetime(2026, 2, 28)
        )

    def test_day_clamps_to_leap_february(self):
        self.assertEqual(
            add_months(datetime(2024, 1, 31), 1), datetime(2024, 2, 29)
        )


class TestNextTarget(unittest.TestCase):
    def test_start_same_year(self):
        now = datetime(2026, 10, 15, 12, 0)
        self.assertEqual(next_target(now, "start"), datetime(2026, 11, 1))

    def test_start_rolls_after_nov_1(self):
        now = datetime(2026, 11, 15, 12, 0)
        self.assertEqual(next_target(now, "start"), datetime(2027, 11, 1))

    def test_start_rolls_at_exact_midnight(self):
        # "The nearest Nov 1 that has NOT happened yet": at exactly
        # Nov 1 00:00 the challenge has begun, so aim for next year.
        now = datetime(2026, 11, 1, 0, 0, 0)
        self.assertEqual(next_target(now, "start"), datetime(2027, 11, 1))

    def test_one_second_before_is_not_rolled(self):
        now = datetime(2026, 10, 31, 23, 59, 59)
        self.assertEqual(next_target(now, "start"), datetime(2026, 11, 1))

    def test_end_during_november(self):
        now = datetime(2026, 11, 15, 12, 0)
        self.assertEqual(next_target(now, "end"), datetime(2026, 12, 1))

    def test_end_rolls_in_december(self):
        now = datetime(2026, 12, 5, 12, 0)
        self.assertEqual(next_target(now, "end"), datetime(2027, 12, 1))

    def test_unknown_mode_raises(self):
        with self.assertRaises(ValueError):
            next_target(datetime(2026, 1, 1), "banana")


class TestRemaining(unittest.TestCase):
    def test_calendar_months_and_remainder(self):
        # Aug 20 10:00 -> Nov 1 00:00:  two full months (to Oct 20 10:00),
        # then 11 days and 14 hours.
        now = datetime(2026, 8, 20, 10, 0, 0)
        target = datetime(2026, 11, 1, 0, 0, 0)
        self.assertEqual(remaining(now, target), (2, 11, 14, 0, 0))

    def test_month_end_clamp_does_not_overshoot(self):
        # Jan 31 12:00 -> Mar 1 00:00: only ONE full month fits
        # (to Feb 28 12:00), remainder is 12 hours, not "2 months".
        now = datetime(2026, 1, 31, 12, 0, 0)
        target = datetime(2026, 3, 1, 0, 0, 0)
        self.assertEqual(remaining(now, target), (1, 0, 12, 0, 0))

    def test_less_than_a_month(self):
        now = datetime(2026, 10, 31, 0, 0, 0)
        target = datetime(2026, 11, 1, 0, 0, 0)
        self.assertEqual(remaining(now, target), (0, 1, 0, 0, 0))

    def test_seconds_component(self):
        now = datetime(2026, 10, 31, 23, 59, 58)
        target = datetime(2026, 11, 1, 0, 0, 0)
        self.assertEqual(remaining(now, target), (0, 0, 0, 0, 2))

    def test_past_target_is_zero(self):
        now = datetime(2026, 11, 2, 0, 0, 0)
        self.assertEqual(
            remaining(now, datetime(2026, 11, 1, 0, 0, 0)), (0, 0, 0, 0, 0)
        )

    def test_full_year_of_months(self):
        # Dec 5 2026 -> Nov 1 2027: 10 full months (to Oct 5), then 27 days.
        now = datetime(2026, 12, 5, 0, 0, 0)
        target = datetime(2027, 11, 1, 0, 0, 0)
        self.assertEqual(remaining(now, target), (10, 27, 0, 0, 0))


class TestChallengeActive(unittest.TestCase):
    def test_inside_november(self):
        self.assertTrue(is_challenge_active(datetime(2026, 11, 15)))
        self.assertTrue(is_challenge_active(datetime(2026, 11, 1, 0, 0)))
        self.assertTrue(is_challenge_active(datetime(2026, 11, 30, 23, 59)))

    def test_outside_november(self):
        self.assertFalse(is_challenge_active(datetime(2026, 10, 31, 23, 59)))
        self.assertFalse(is_challenge_active(datetime(2026, 12, 1, 0, 0)))


class TestTimezoneName(unittest.TestCase):
    def test_returns_non_empty_string(self):
        self.assertTrue(timezone_name())


if __name__ == "__main__":
    unittest.main()

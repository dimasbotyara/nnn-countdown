"""Countdown target and remaining-time math for NNN Countdown.

All calculations use local wall-clock time via ``datetime.now()`` /
naive local datetimes, so DST transitions and any OS timezone are handled
by the operating system, not by us.
"""
import calendar
import os
from datetime import datetime

MODE_START = "start"  # countdown to the beginning of the challenge (Nov 1)
MODE_END = "end"      # countdown to the end of the challenge (Dec 1)

MODES = (MODE_START, MODE_END)

# Target month for each mode: Nov 1st 00:00 or Dec 1st 00:00 local time.
_TARGET_MONTH = {MODE_START: 11, MODE_END: 12}


def add_months(dt, months):
    """Return ``dt`` shifted by ``months`` calendar months.

    The day is clamped to the last day of the resulting month
    (e.g. Jan 31 + 1 month -> Feb 28/29).
    """
    index = dt.year * 12 + (dt.month - 1) + months
    year, month0 = divmod(index, 12)
    day = min(dt.day, calendar.monthrange(year, month0 + 1)[1])
    return dt.replace(year=year, month=month0 + 1, day=day)


def next_target(now, mode):
    """Return the nearest future target datetime for ``mode``.

    MODE_START -> nearest Nov 1 00:00:00 that has not happened yet.
    MODE_END   -> nearest Dec 1 00:00:00 that has not happened yet.
    """
    if mode not in MODES:
        raise ValueError(f"unknown mode: {mode!r}")
    target = now.replace(
        month=_TARGET_MONTH[mode], day=1,
        hour=0, minute=0, second=0, microsecond=0,
    )
    if target <= now:
        target = target.replace(year=target.year + 1)
    return target


def remaining(now, target):
    """Calendar-accurate remainder between ``now`` and ``target``.

    Returns ``(months, days, hours, minutes, seconds)`` where ``months``
    is the number of *full calendar months* that fit between now and the
    target, and the rest is a plain timedelta remainder.
    """
    if target <= now:
        return (0, 0, 0, 0, 0)
    months = max((target.year - now.year) * 12 + (target.month - now.month), 0)
    # Whole-month count may overshoot near month ends (e.g. Jan 31 -> Mar 1).
    if months and add_months(now, months) > target:
        months -= 1
    anchor = add_months(now, months)
    delta = target - anchor
    days = delta.days
    hours, rem = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return (months, days, hours, minutes, seconds)


def is_challenge_active(now):
    """True when ``now`` falls inside November 1-30 (local time)."""
    return now.month == 11 and 1 <= now.day <= 30


def timezone_name():
    """Best-effort human name of the local timezone.

    Prefers an IANA name (e.g. "Europe/Moscow") extracted from the
    /etc/localtime symlink or the TZ variable; falls back to whatever
    abbreviation the platform reports (e.g. "MSK").
    """
    try:
        link = os.path.realpath("/etc/localtime")
        marker = "zoneinfo/"
        if marker in link:
            tail = link.split(marker, 1)[1]
            if tail:
                return tail
    except OSError:
        pass
    env_tz = os.environ.get("TZ", "").strip()
    if env_tz and "/" in env_tz:
        return env_tz
    name = datetime.now().astimezone().tzname()
    return name or "local"

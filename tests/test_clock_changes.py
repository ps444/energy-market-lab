# Tests for clock-change (DST) handling.
#
# The expected values come from Python's own time-zone database (zoneinfo),
# not from the code under test, so they are an independent check.

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from main import find_last_sunday, is_dst_day, period_start_time

TIME_ZONES = {"UK": "Europe/London", "France": "Europe/Paris"}
YEARS = [2024, 2025, 2026, 2027]


def expected_start_times(day, minutes_per_period, tz_name):
    """Local (hour, minute) of every period start, from the time-zone database."""
    tz = ZoneInfo(tz_name)
    start = datetime(day.year, day.month, day.day, tzinfo=tz).astimezone(timezone.utc)
    next_day = day + timedelta(days=1)
    end = datetime(next_day.year, next_day.month, next_day.day, tzinfo=tz).astimezone(timezone.utc)

    times = []
    current = start
    while current < end:
        local = current.astimezone(tz)
        times.append((local.hour, local.minute))
        current += timedelta(minutes=minutes_per_period)
    return times


def days_to_check(year):
    return [
        date(year, 3, find_last_sunday(year, 3)),    # short day
        date(year, 10, find_last_sunday(year, 10)),  # long day
        date(year, 6, 15),                           # normal day
    ]


def test_find_last_sunday():
    assert find_last_sunday(2023, 3) == 26
    assert find_last_sunday(2026, 3) == 29
    assert find_last_sunday(2026, 10) == 25
    assert find_last_sunday(2026, 12) == 27


@pytest.mark.parametrize("location", TIME_ZONES)
def test_is_dst_day(location):
    assert is_dst_day("2026-03-29", location) == "short"
    assert is_dst_day("2026-10-25", location) == "long"
    assert is_dst_day("2026-06-15", location) == "normal"


def test_unsupported_location_is_rejected():
    with pytest.raises(ValueError):
        is_dst_day("2026-10-25", "Germany")


@pytest.mark.parametrize("location", TIME_ZONES)
@pytest.mark.parametrize("year", YEARS)
@pytest.mark.parametrize("minutes_per_period", [60, 30])
def test_period_start_times_match_time_zone_database(location, year, minutes_per_period):
    for day in days_to_check(year):
        expected = expected_start_times(day, minutes_per_period, TIME_ZONES[location])
        dst_type = is_dst_day(day.isoformat(), location)

        actual = [
            period_start_time(period, minutes_per_period, dst_type, location)
            for period in range(len(expected))
        ]

        assert actual == expected, f"{location} {day} ({dst_type}), {minutes_per_period}-minute periods"


@pytest.mark.parametrize("location", TIME_ZONES)
def test_period_counts(location):
    # 23/24/25 hourly and 46/48/50 half-hourly, as used in main.py
    counts = {"short": 23, "normal": 24, "long": 25}
    for day in days_to_check(2026):
        dst_type = is_dst_day(day.isoformat(), location)
        assert len(expected_start_times(day, 60, TIME_ZONES[location])) == counts[dst_type]
        assert len(expected_start_times(day, 30, TIME_ZONES[location])) == counts[dst_type] * 2

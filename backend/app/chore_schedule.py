from datetime import datetime, timedelta
from typing import Iterable

from app.chore_template import (
    ChoreTemplateResponse,
    RepeatType,
)

"""
Module for recurring chore schedule calculations.

Contributors: Edmund Krajewski
"""


def _to_datetime(value: str | None) -> datetime | None:
    """
    Convert an ISO datetime string to a datetime object.
    Returns None if value is None.
    """
    if value is None:
        return None
    return datetime.fromisoformat(value)


def _normalize_weekday_list(days: list[int] | None) -> list[int]:
    """
    Normalize repeat_days_of_week into a sorted unique list of valid weekdays.
    Monday = 0, Sunday = 6.
    """
    if days is None:
        return []

    normalized = sorted(set(days))

    for day in normalized:
        if day < 0 or day > 6:
            raise ValueError("repeat_days_of_week must contain values from 0 to 6.")

    return normalized


def _is_past_end_date(template: ChoreTemplateResponse, target: datetime) -> bool:
    """
    Return True if the target date is after the template end_date.
    """
    end_date = _to_datetime(template.end_date)
    if end_date is None:
        return False

    return target.date() > end_date.date()


def _matches_daily(template: ChoreTemplateResponse, target: datetime) -> bool:
    """
    Match DAILY recurrence using repeat_interval days from start_date.
    """
    start_date = _to_datetime(template.start_date)
    if start_date is None or target.date() < start_date.date():
        return False

    delta_days = (target.date() - start_date.date()).days
    return delta_days % template.repeat_interval == 0


def _matches_weekday(template: ChoreTemplateResponse, target: datetime) -> bool:
    """
    Match WEEKDAY recurrence on Monday-Friday.
    Currently repeat_interval is treated as every weekday cycle day-by-day.
    """
    start_date = _to_datetime(template.start_date)
    if start_date is None or target.date() < start_date.date():
        return False

    if target.weekday() >= 5:
        return False

    if template.repeat_interval == 1:
        return True

    delta_days = (target.date() - start_date.date()).days
    return delta_days % template.repeat_interval == 0


def _matches_weekly(template: ChoreTemplateResponse, target: datetime) -> bool:
    """
    Match WEEKLY recurrence using repeat_interval weeks and repeat_days_of_week.
    If repeat_days_of_week is empty, fall back to the start_date weekday.
    """
    start_date = _to_datetime(template.start_date)
    if start_date is None or target.date() < start_date.date():
        return False

    days_of_week = _normalize_weekday_list(template.repeat_days_of_week)
    if not days_of_week:
        days_of_week = [start_date.weekday()]

    if target.weekday() not in days_of_week:
        return False

    delta_days = (target.date() - start_date.date()).days
    week_offset = delta_days // 7
    return week_offset % template.repeat_interval == 0


def _matches_monthly(template: ChoreTemplateResponse, target: datetime) -> bool:
    """
    Match MONTHLY recurrence on a specific day of month.
    Falls back to the start_date day if repeat_day_of_month is not set.
    """
    start_date = _to_datetime(template.start_date)
    if start_date is None or target.date() < start_date.date():
        return False

    day_of_month = template.repeat_day_of_month or start_date.day

    if target.day != day_of_month:
        return False

    months_apart = (target.year - start_date.year) * 12 + (target.month - start_date.month)
    return months_apart % template.repeat_interval == 0


def _matches_custom(template: ChoreTemplateResponse, target: datetime) -> bool:
    """
    For now, CUSTOM behaves like WEEKLY with explicit repeat_days_of_week.
    This gives you Finch-style 'specific days of the week' behavior without
    building a full RRULE system.
    """
    return _matches_weekly(template, target)


def is_due_on_date(template: ChoreTemplateResponse, target: datetime) -> bool:
    """
    Return True if the recurring template is due on the target date.
    """
    if not template.is_active:
        return False

    start_date = _to_datetime(template.start_date)
    if start_date is None:
        return False

    if target.date() < start_date.date():
        return False

    if _is_past_end_date(template, target):
        return False

    repeat_type = template.repeat_type

    if repeat_type == RepeatType.DAILY.value:
        return _matches_daily(template, target)

    if repeat_type == RepeatType.WEEKDAY.value:
        return _matches_weekday(template, target)

    if repeat_type == RepeatType.WEEKLY.value:
        return _matches_weekly(template, target)

    if repeat_type == RepeatType.MONTHLY.value:
        return _matches_monthly(template, target)

    if repeat_type == RepeatType.CUSTOM.value:
        return _matches_custom(template, target)

    raise ValueError(f"Unsupported repeat_type: {repeat_type}")


def get_due_dates_in_range(
    template: ChoreTemplateResponse,
    range_start: datetime,
    range_end: datetime,
) -> list[datetime]:
    """
    Return all due dates for a template in the inclusive date range.
    """
    if range_end < range_start:
        raise ValueError("range_end must be greater than or equal to range_start.")

    due_dates: list[datetime] = []

    current = range_start
    while current.date() <= range_end.date():
        if is_due_on_date(template, current):
            due_dates.append(current)
        current += timedelta(days=1)

    return due_dates


def get_generation_window(now: datetime, preview_days: int) -> tuple[datetime, datetime]:
    """
    Return the generation window used for creating upcoming chores.

    Example:
        now = April 19
        preview_days = 1
        => generate chores due from April 19 through April 20
    """
    if preview_days < 0:
        raise ValueError("preview_days cannot be negative.")

    range_start = now
    range_end = now + timedelta(days=preview_days)
    return range_start, range_end


def get_due_dates_to_generate(
    template: ChoreTemplateResponse,
    now: datetime,
) -> list[datetime]:
    """
    Return due dates that should exist by now for this template, based on preview_days.
    """
    range_start, range_end = get_generation_window(now, template.preview_days)
    return get_due_dates_in_range(template, range_start, range_end)
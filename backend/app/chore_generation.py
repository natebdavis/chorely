from datetime import datetime, timedelta, timezone
from typing import Union

from supabase import Client

from app.chore import (
    ChoreCreateRequest,
    ChoreResponse,
    CHORE_TABLE_NAME,
    Chore_Col_Name,
    Status,
    CalendarDateMetaResponse,
    ChoreRangeResponse,
)
from app.chore_template import ChoreTemplateResponse
from app.chore_schedule import get_due_dates_in_range
from app.db.chore_repo import add_chore
from app.db.chore_template_repo import get_chore_templates
from app.db.client import get_client

"""
Module for generating chore instances from recurring chore templates
and preparing range-based calendar responses.

Contributor: Edmund Krajewski
"""


def _normalize_datetime(value: datetime) -> datetime:
    """
    Normalize datetimes so comparisons are always safe.

    If a datetime is naive, treat it as UTC.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _to_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None
    return _normalize_datetime(datetime.fromisoformat(value))


def _date_key(value: datetime | str) -> str:
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    value = _normalize_datetime(value)
    return value.date().isoformat()


def _daterange(start: datetime, end: datetime):
    start = _normalize_datetime(start)
    end = _normalize_datetime(end)

    current = start
    while current.date() <= end.date():
        yield current
        current += timedelta(days=1)


def _build_due_datetime(
    template: ChoreTemplateResponse,
    scheduled_day: datetime,
) -> datetime:
    start_dt = _to_datetime(template.start_date)
    if start_dt is None:
        raise ValueError("Template start_date is required.")

    scheduled_day = _normalize_datetime(scheduled_day)

    return datetime(
        year=scheduled_day.year,
        month=scheduled_day.month,
        day=scheduled_day.day,
        hour=start_dt.hour,
        minute=start_dt.minute,
        second=start_dt.second,
        microsecond=start_dt.microsecond,
        tzinfo=start_dt.tzinfo,
    )


def chore_instance_exists(
    templateid: int,
    due_date: datetime,
    client: Union[Client, None] = None,
) -> bool:
    if client is None:
        client = get_client()

    due_date = _normalize_datetime(due_date)

    response = (
        client
        .table(CHORE_TABLE_NAME)
        .select(Chore_Col_Name.choreid.value)
        .eq(Chore_Col_Name.template_id.value, templateid)
        .eq(Chore_Col_Name.due_date.value, due_date.isoformat())
        .limit(1)
        .execute()
    )

    return bool(response.data)


def generate_chore_from_template(
    template: ChoreTemplateResponse,
    due_date: datetime,
    client: Union[Client, None] = None,
):
    if client is None:
        client = get_client()

    due_date = _normalize_datetime(due_date)

    status = Status.IN_PROGRESS.name if template.assignee_id else Status.UNASSIGNED.name

    chore_request = ChoreCreateRequest(
        householdid=template.householdid,
        name=template.name,
        description=template.description,
        request_date=datetime.now(timezone.utc).isoformat(),
        due_date=due_date.isoformat(),
        requester_id=template.created_by,
        assignee_id=template.assignee_id,
        template_id=template.templateid,
        status=status,
        priority=template.priority,
        ctype=template.ctype,
        location=template.location,
    )

    return add_chore(chore_request, client=client)


def generate_due_chores_for_household_in_range(
    householdid: int,
    range_start: datetime,
    range_end: datetime,
    client: Union[Client, None] = None,
) -> int:
    if client is None:
        client = get_client()

    range_start = _normalize_datetime(range_start)
    range_end = _normalize_datetime(range_end)

    templates = list(get_chore_templates(householdid=householdid, active_only=True, client=client))
    created_count = 0

    for template in templates:
        due_days = get_due_dates_in_range(template, range_start, range_end)

        for due_day in due_days:
            due_datetime = _build_due_datetime(template, due_day)

            if chore_instance_exists(template.templateid, due_datetime, client=client):
                continue

            created = generate_chore_from_template(template, due_datetime, client=client)

            if created:
                created_count += 1

    return created_count


def build_chores_by_date(
    chores: list[ChoreResponse],
    range_start: datetime,
    range_end: datetime,
) -> dict[str, list[ChoreResponse]]:
    chores_by_date = {
        day.date().isoformat(): [] for day in _daterange(range_start, range_end)
    }

    for chore in chores:
        if chore.due_date is None:
            continue

        key = _date_key(chore.due_date)
        if key not in chores_by_date:
            chores_by_date[key] = []

        chores_by_date[key].append(chore)

    return chores_by_date


def build_calendar_meta(
    chores: list[ChoreResponse],
    range_start: datetime,
    range_end: datetime,
    now: Union[datetime, None] = None,
    current_user_id: Union[int, None] = None,
) -> dict[str, CalendarDateMetaResponse]:

    if now is None:
        now = datetime.now(timezone.utc)

    now = _normalize_datetime(now)

    calendar_meta = {
        day.date().isoformat(): CalendarDateMetaResponse()
        for day in _daterange(range_start, range_end)
    }

    for chore in chores:
        if chore.due_date is None:
            continue

        due_dt = _to_datetime(chore.due_date)
        if due_dt is None:
            continue

        key = due_dt.date().isoformat()
        if key not in calendar_meta:
            continue

        meta = calendar_meta[key]

        meta.chore_count += 1
        meta.has_chores = True

        if chore.status != Status.COMPLETE.name:
            meta.has_incomplete = True

        if due_dt < now and chore.status != Status.COMPLETE.name:
            meta.has_overdue = True

        if current_user_id is not None and chore.assignee_id == current_user_id:
            meta.has_assigned_to_me = True

        if chore.priority == "HIGH":
            meta.has_high_priority = True

    return calendar_meta


def build_chore_range_response(
    chores: list[ChoreResponse],
    range_start: datetime,
    range_end: datetime,
    now: Union[datetime, None] = None,
    current_user_id: Union[int, None] = None,
) -> ChoreRangeResponse:

    return ChoreRangeResponse(
        chores_by_date=build_chores_by_date(chores, range_start, range_end),
        calendar_meta=build_calendar_meta(
            chores,
            range_start,
            range_end,
            now=now,
            current_user_id=current_user_id,
        ),
    )
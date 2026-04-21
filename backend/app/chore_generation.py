from datetime import datetime
from typing import Union

from supabase import Client

from app.chore import ChoreCreateRequest, CHORE_TABLE_NAME, Chore_Col_Name, Status
from app.chore_template import ChoreTemplateResponse
from app.chore_schedule import get_due_dates_to_generate
from app.db.chore_repo import add_chore
from app.db.chore_template_repo import get_chore_templates
from app.db.client import get_client

"""
Module for generating chore instances from recurring chore templates.

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


def _build_due_datetime(
    template: ChoreTemplateResponse,
    scheduled_day: datetime,
) -> datetime:
    """
    Build the concrete due datetime for a generated chore instance.

    Uses the time component from template.start_date and the calendar date from
    the scheduled due day.
    """
    start_dt = _to_datetime(template.start_date)
    if start_dt is None:
        raise ValueError("Template start_date is required.")

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
    """
    Check whether a chore instance already exists for a template and due date.
    """
    if client is None:
        client = get_client()

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
    """
    Generate a single chore instance from a recurring chore template.

    Output:
        The created ChoreResponse, or None if creation failed.
    """
    if client is None:
        client = get_client()

    status = Status.IN_PROGRESS.name if template.assignee_id is not None else Status.UNASSIGNED.name

    chore_request = ChoreCreateRequest(
        householdid=template.householdid,
        name=template.name,
        description=template.description,
        request_date=datetime.now(tz=due_date.tzinfo).isoformat(),
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


def generate_due_chores_for_household(
    householdid: int,
    now: Union[datetime, None] = None,
    client: Union[Client, None] = None,
) -> int:
    """
    Generate any missing chore instances for active recurring templates
    in the household.

    Output:
        Number of new chore instances created.
    """
    if client is None:
        client = get_client()

    if now is None:
        now = datetime.now()

    templates = list(get_chore_templates(householdid=householdid, active_only=True, client=client))

    created_count = 0

    for template in templates:
        due_days = get_due_dates_to_generate(template, now)

        for due_day in due_days:
            due_datetime = _build_due_datetime(template, due_day)

            if chore_instance_exists(template.templateid, due_datetime, client=client):
                continue

            created = generate_chore_from_template(template, due_datetime, client=client)

            if created is not None:
                created_count += 1

    return created_count
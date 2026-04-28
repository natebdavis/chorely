"""
Module for recurring chore template-related database operations.

Contributors: Edmund Krajewski
"""

from collections.abc import Iterable
from typing import Union

from supabase import Client

from app.chore_template import (
    CHORE_TEMPLATE_TABLE_NAME,
    ChoreTemplate_Col_Name,
    ChoreTemplateCreateRequest,
    ChoreTemplateResponse,
    ChoreTemplateUpdateRequest,
    create_ChoreTemplateResponse,
)
from app.db.client import get_client

first = 0


def get_chore_template(
    templateid: int,
    client: Union[Client, None] = None,
) -> Union[ChoreTemplateResponse, None]:
    """
    Get a single recurring chore template given a templateid.

    Output:
        A ChoreTemplateResponse matching the templateid, or None if not found.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(CHORE_TEMPLATE_TABLE_NAME)
        .select("*")
        .eq(ChoreTemplate_Col_Name.templateid.value, templateid)
        .execute()
    )

    data = response.data
    if not data:
        return None

    return create_ChoreTemplateResponse(data[first])


def get_chore_templates(
    householdid: int,
    active_only: bool = False,
    client: Union[Client, None] = None,
) -> Iterable[ChoreTemplateResponse]:
    """
    Get all recurring chore templates in a household.

    Output:
        An iterable of ChoreTemplateResponse objects in the specified household.
    """
    if client is None:
        client = get_client()

    query = (
        client
        .table(CHORE_TEMPLATE_TABLE_NAME)
        .select("*")
        .eq(ChoreTemplate_Col_Name.householdid.value, householdid)
    )

    if active_only:
        query = query.eq(ChoreTemplate_Col_Name.is_active.value, True)

    response = query.execute()

    data = response.data or []
    return [create_ChoreTemplateResponse(row) for row in data]


def add_chore_template(
    template: ChoreTemplateCreateRequest,
    client: Union[Client, None] = None,
) -> Union[ChoreTemplateResponse, None]:
    """
    Add a recurring chore template to the database.

    Output:
        Inserted recurring chore template data returned as ChoreTemplateResponse,
        or None if insert failed.
    """
    if client is None:
        client = get_client()

    data = {
        ChoreTemplate_Col_Name.householdid.value: template.householdid,
        ChoreTemplate_Col_Name.created_by.value: template.created_by,
        ChoreTemplate_Col_Name.assignee_id.value: template.assignee_id,
        ChoreTemplate_Col_Name.name.value: template.name,
        ChoreTemplate_Col_Name.description.value: template.description,
        ChoreTemplate_Col_Name.start_date.value: template.start_date,
        ChoreTemplate_Col_Name.end_date.value: template.end_date,
        ChoreTemplate_Col_Name.time_bucket.value: template.time_bucket,
        ChoreTemplate_Col_Name.repeat_type.value: template.repeat_type,
        ChoreTemplate_Col_Name.repeat_interval.value: template.repeat_interval,
        ChoreTemplate_Col_Name.repeat_days_of_week.value: template.repeat_days_of_week,
        ChoreTemplate_Col_Name.repeat_day_of_month.value: template.repeat_day_of_month,
        ChoreTemplate_Col_Name.is_active.value: template.is_active,
        ChoreTemplate_Col_Name.last_generated_at.value: template.last_generated_at,
        ChoreTemplate_Col_Name.priority.value: template.priority,
        ChoreTemplate_Col_Name.ctype.value: template.ctype,
        ChoreTemplate_Col_Name.location.value: template.location,
    }

    response = client.table(CHORE_TEMPLATE_TABLE_NAME).insert(data).execute()
    rows = response.data

    if not rows:
        return None

    return create_ChoreTemplateResponse(rows[first])


def update_chore_template(
    templateid: int,
    template: ChoreTemplateUpdateRequest,
    client: Union[Client, None] = None,
) -> Union[ChoreTemplateResponse, None]:
    """
    Update an existing recurring chore template in the database.

    Output:
        Updated recurring chore template returned as ChoreTemplateResponse,
        or None if update failed.
    """
    if client is None:
        client = get_client()

    fields_set = getattr(template, "model_fields_set", set())

    data = {}

    if "name" in fields_set:
        data[ChoreTemplate_Col_Name.name.value] = template.name
    if "description" in fields_set:
        data[ChoreTemplate_Col_Name.description.value] = template.description
    if "start_date" in fields_set:
        data[ChoreTemplate_Col_Name.start_date.value] = template.start_date
    if "end_date" in fields_set:
        data[ChoreTemplate_Col_Name.end_date.value] = template.end_date
    if "assignee_id" in fields_set:
        data[ChoreTemplate_Col_Name.assignee_id.value] = template.assignee_id
    if "time_bucket" in fields_set:
        data[ChoreTemplate_Col_Name.time_bucket.value] = template.time_bucket
    if "repeat_type" in fields_set:
        data[ChoreTemplate_Col_Name.repeat_type.value] = template.repeat_type
    if "repeat_interval" in fields_set:
        data[ChoreTemplate_Col_Name.repeat_interval.value] = template.repeat_interval
    if "repeat_days_of_week" in fields_set:
        data[ChoreTemplate_Col_Name.repeat_days_of_week.value] = template.repeat_days_of_week
    if "repeat_day_of_month" in fields_set:
        data[ChoreTemplate_Col_Name.repeat_day_of_month.value] = template.repeat_day_of_month
    if "is_active" in fields_set:
        data[ChoreTemplate_Col_Name.is_active.value] = template.is_active
    if "last_generated_at" in fields_set:
        data[ChoreTemplate_Col_Name.last_generated_at.value] = template.last_generated_at
    if "priority" in fields_set:
        data[ChoreTemplate_Col_Name.priority.value] = template.priority
    if "ctype" in fields_set:
        data[ChoreTemplate_Col_Name.ctype.value] = template.ctype
    if "location" in fields_set:
        data[ChoreTemplate_Col_Name.location.value] = template.location

    if not data:
        return get_chore_template(templateid=templateid, client=client)

    response = (
        client
        .table(CHORE_TEMPLATE_TABLE_NAME)
        .update(data)
        .eq(ChoreTemplate_Col_Name.templateid.value, templateid)
        .execute()
    )

    rows = response.data
    if not rows:
        return None

    return create_ChoreTemplateResponse(rows[first])


def deactivate_chore_template(
    templateid: int,
    client: Union[Client, None] = None,
) -> Union[ChoreTemplateResponse, None]:
    """
    Mark a recurring chore template as inactive.

    Output:
        Updated recurring chore template returned as ChoreTemplateResponse,
        or None if update failed.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(CHORE_TEMPLATE_TABLE_NAME)
        .update({ChoreTemplate_Col_Name.is_active.value: False})
        .eq(ChoreTemplate_Col_Name.templateid.value, templateid)
        .execute()
    )

    rows = response.data
    if not rows:
        return None

    return create_ChoreTemplateResponse(rows[first])
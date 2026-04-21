from enum import Enum
from typing import Union

from pydantic import BaseModel, Field

"""
Module for managing recurring Chore Template operations.

Contributors: Edmund Krajewski
"""

CHORE_TEMPLATE_TABLE_NAME = "chore_templates"


class ChoreTemplate_Col_Name(Enum):
    """Column names for recurring chore template database table."""
    templateid = "templateid"
    householdid = "householdid"
    created_by = "created_by"
    assignee_id = "assignee_id"
    name = "name"
    description = "description"
    start_date = "start_date"
    end_date = "end_date"
    time_bucket = "time_bucket"
    repeat_type = "repeat_type"
    repeat_interval = "repeat_interval"
    repeat_days_of_week = "repeat_days_of_week"
    repeat_day_of_month = "repeat_day_of_month"
    is_active = "is_active"
    last_generated_at = "last_generated_at"
    priority = "priority"
    location = "location"
    ctype = "ctype"
    created_at = "created_at"


class RepeatType(str, Enum):
    DAILY = "DAILY"
    WEEKDAY = "WEEKDAY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    CUSTOM = "CUSTOM"


class TimeBucket(str, Enum):
    START_OF_DAY = "START_OF_DAY"
    AFTERNOON = "AFTERNOON"
    EVENING = "EVENING"
    BEDTIME = "BEDTIME"
    ANYTIME = "ANYTIME"


class ChoreTemplateCreateInput(BaseModel):
    """
    Request body schema for creating a recurring chore template from the frontend.
    """
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=3000)
    start_date: str
    end_date: Union[str, None] = None
    assignee_id: Union[int, None] = None
    time_bucket: TimeBucket = TimeBucket.ANYTIME
    repeat_type: RepeatType
    repeat_interval: int = Field(default=1, ge=1)
    repeat_days_of_week: Union[list[int], None] = None
    repeat_day_of_month: Union[int, None] = Field(default=None, ge=1, le=31)
    priority: Union[str, None] = None
    ctype: Union[str, None] = None
    location: Union[str, None] = None


class ChoreTemplateCreateRequest(BaseModel):
    """
    Internal request schema used by the backend/database layer
    when creating a recurring chore template.
    """
    householdid: int
    created_by: int
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=3000)
    start_date: str
    end_date: Union[str, None] = None
    assignee_id: Union[int, None] = None
    time_bucket: str
    repeat_type: str
    repeat_interval: int = Field(default=1, ge=1)
    repeat_days_of_week: Union[list[int], None] = None
    repeat_day_of_month: Union[int, None] = Field(default=None, ge=1, le=31)
    is_active: bool = True
    last_generated_at: Union[str, None] = None
    priority: Union[str, None] = None
    ctype: Union[str, None] = None
    location: Union[str, None] = None


class ChoreTemplateUpdateRequest(BaseModel):
    """
    Request body schema for updating an existing recurring chore template.
    """
    name: Union[str, None] = Field(default=None, min_length=1, max_length=50)
    description: Union[str, None] = Field(default=None, min_length=1, max_length=3000)
    start_date: Union[str, None] = None
    end_date: Union[str, None] = None
    assignee_id: Union[int, None] = None
    time_bucket: Union[str, None] = None
    repeat_type: Union[str, None] = None
    repeat_interval: Union[int, None] = Field(default=None, ge=1)
    repeat_days_of_week: Union[list[int], None] = None
    repeat_day_of_month: Union[int, None] = Field(default=None, ge=1, le=31)
    is_active: Union[bool, None] = None
    last_generated_at: Union[str, None] = None
    priority: Union[str, None] = None
    ctype: Union[str, None] = None
    location: Union[str, None] = None


class ChoreTemplateResponse(BaseModel):
    """
    Response schema returned for recurring chore template API requests.
    """
    templateid: int
    householdid: int
    created_by: int
    assignee_id: Union[int, None] = None
    name: str
    description: str
    start_date: str
    end_date: Union[str, None] = None
    time_bucket: str
    repeat_type: str
    repeat_interval: int
    repeat_days_of_week: Union[list[int], None] = None
    repeat_day_of_month: Union[int, None] = None
    is_active: bool
    last_generated_at: Union[str, None] = None
    priority: Union[str, None] = None
    ctype: Union[str, None] = None
    location: Union[str, None] = None
    created_at: str


def create_ChoreTemplateCreateRequest(data: dict) -> ChoreTemplateCreateRequest:
    return ChoreTemplateCreateRequest(
        householdid=data[ChoreTemplate_Col_Name.householdid.value],
        created_by=data[ChoreTemplate_Col_Name.created_by.value],
        name=data[ChoreTemplate_Col_Name.name.value],
        description=data[ChoreTemplate_Col_Name.description.value],
        start_date=data[ChoreTemplate_Col_Name.start_date.value],
        end_date=data.get(ChoreTemplate_Col_Name.end_date.value),
        assignee_id=data.get(ChoreTemplate_Col_Name.assignee_id.value),
        time_bucket=data[ChoreTemplate_Col_Name.time_bucket.value],
        repeat_type=data[ChoreTemplate_Col_Name.repeat_type.value],
        repeat_interval=data[ChoreTemplate_Col_Name.repeat_interval.value],
        repeat_days_of_week=data.get(ChoreTemplate_Col_Name.repeat_days_of_week.value),
        repeat_day_of_month=data.get(ChoreTemplate_Col_Name.repeat_day_of_month.value),
        is_active=data.get(ChoreTemplate_Col_Name.is_active.value, True),
        last_generated_at=data.get(ChoreTemplate_Col_Name.last_generated_at.value),
        priority=data.get(ChoreTemplate_Col_Name.priority.value),
        ctype=data.get(ChoreTemplate_Col_Name.ctype.value),
        location=data.get(ChoreTemplate_Col_Name.location.value),
    )


def create_ChoreTemplateResponse(data: dict) -> ChoreTemplateResponse:
    return ChoreTemplateResponse(
        templateid=data[ChoreTemplate_Col_Name.templateid.value],
        householdid=data[ChoreTemplate_Col_Name.householdid.value],
        created_by=data[ChoreTemplate_Col_Name.created_by.value],
        assignee_id=data.get(ChoreTemplate_Col_Name.assignee_id.value),
        name=data[ChoreTemplate_Col_Name.name.value],
        description=data[ChoreTemplate_Col_Name.description.value],
        start_date=data[ChoreTemplate_Col_Name.start_date.value],
        end_date=data.get(ChoreTemplate_Col_Name.end_date.value),
        time_bucket=data[ChoreTemplate_Col_Name.time_bucket.value],
        repeat_type=data[ChoreTemplate_Col_Name.repeat_type.value],
        repeat_interval=data[ChoreTemplate_Col_Name.repeat_interval.value],
        repeat_days_of_week=data.get(ChoreTemplate_Col_Name.repeat_days_of_week.value),
        repeat_day_of_month=data.get(ChoreTemplate_Col_Name.repeat_day_of_month.value),
        is_active=data[ChoreTemplate_Col_Name.is_active.value],
        last_generated_at=data.get(ChoreTemplate_Col_Name.last_generated_at.value),
        priority=data.get(ChoreTemplate_Col_Name.priority.value),
        ctype=data.get(ChoreTemplate_Col_Name.ctype.value),
        location=data.get(ChoreTemplate_Col_Name.location.value),
        created_at=data[ChoreTemplate_Col_Name.created_at.value],
    )
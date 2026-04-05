from enum import Enum, auto
from pydantic import BaseModel, Field
from typing import Union
from datetime import datetime

from app.user import UserResponse, get_full_name

"""
Module for managing Chore operations.
Contributers: Gilligan Berlinski, Nathaniel Davis, Edmund Krajewski
"""

CHORE_TABLE_NAME = "chores"


class ChoreCreateInput(BaseModel):
    """
    Request body schema for creating a new chore from the frontend.
    """
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=3000)
    due_date: str
    assignee_id: Union[int, None] = None


class ChoreCreateRequest(BaseModel):
    """
    Internal request schema used by the backend/database layer
    when creating a new chore.
    """
    householdid: int
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=3000)
    request_date: str
    due_date: str
    requester_id: int
    assignee_id: Union[int, None] = None
    status: str


class ChoreUpdateRequest(BaseModel):
    """
    Request body schema for updating a Chore.
    """
    status: Union[str, None] = None
    assignee_id: Union[int, None] = None


class ChoreDeleteRequest(BaseModel):
    """
    Request body schema for deleting a Chore.
    """
    choreid: int


class ChoreResponse(BaseModel):
    """
    Response schema returned for Chore-related API requests.
    """
    householdid: int
    choreid: int
    name: str
    description: str
    request_date: Union[str, None] = None
    due_date: Union[str, None] = None
    requester_id: Union[int, None] = None
    assignee_id: Union[int, None] = None
    assignee: Union[str, None] = None
    status: Union[str, None] = None


class Chore_Col_Name(Enum):
    """Column names for Chore database table."""
    choreid = "choreid"
    cname = "cname"
    description = "descrip"
    request_date = "request_date"
    due_date = "due_date"
    requester = "request_user"
    assignee = "assigned_user"
    status = "cstatus"
    householdid = "householdid"


class Status(Enum):
    """Status of Chore."""
    UNASSIGNED = auto()
    IN_PROGRESS = auto()
    COMPLETE = auto()
    CANCELLED = auto()


def create_ChoreCreateRequest(data: dict) -> ChoreCreateRequest:
    status = Status.IN_PROGRESS.name if data[Chore_Col_Name.assignee.value] else Status.UNASSIGNED.name

    return ChoreCreateRequest(
        householdid=data[Chore_Col_Name.householdid.value],
        name=data[Chore_Col_Name.cname.value],
        description=data[Chore_Col_Name.description.value],
        request_date=datetime.now().isoformat(),
        due_date=data[Chore_Col_Name.due_date.value],
        requester_id=data[Chore_Col_Name.requester.value],
        assignee_id=data[Chore_Col_Name.assignee.value],
        status=status,
    )


def create_ChoreUpdateRequest(data: dict) -> ChoreUpdateRequest:
    status = data[Chore_Col_Name.status.value]
    assignee = data[Chore_Col_Name.assignee.value]

    if is_valid_status(status=status, assignee=assignee):
        return ChoreUpdateRequest(
            status=status,
            assignee_id=assignee,
        )

    return None


def create_ChoreDeleteRequest(data: dict) -> ChoreDeleteRequest:
    return ChoreDeleteRequest(
        choreid=data[Chore_Col_Name.choreid.value]
    )


def create_ChoreResponse(data: dict, assignee: Union[UserResponse, None] = None) -> ChoreResponse:
    assignee_name = get_full_name(assignee) if assignee else None

    return ChoreResponse(
        householdid=data[Chore_Col_Name.householdid.value],
        choreid=data[Chore_Col_Name.choreid.value],
        name=data[Chore_Col_Name.cname.value],
        description=data[Chore_Col_Name.description.value],
        request_date=data[Chore_Col_Name.request_date.value],
        due_date=data[Chore_Col_Name.due_date.value],
        requester_id=data[Chore_Col_Name.requester.value],
        assignee_id=data[Chore_Col_Name.assignee.value],
        assignee=assignee_name,
        status=data[Chore_Col_Name.status.value],
    )


def is_valid_status(status: str, assignee: Union[int, None] = None) -> bool:
    status = status.upper()

    if status not in Status.__members__:
        raise ValueError("Not a valid Status Type.")

    if assignee and status == Status.UNASSIGNED.name:
        raise ValueError("Cannot be given status UNASSIGNED if assignee exists.")

    if not assignee and status == Status.IN_PROGRESS.name:
        raise ValueError("Cannot be given status IN_PROGRESS if assignee does not exist.")

    return True
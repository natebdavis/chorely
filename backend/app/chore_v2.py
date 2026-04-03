from enum import Enum, auto
from pydantic import BaseModel, Field
from typing import Union
from datetime import datetime

from app.user_v2 import UserResponse, get_full_name

"""
Module for managing Chore operations.
Contributers: Gilligan Berlinski, Nathaniel Davis, Edmund Krajewski
"""

class ChoreCreateRequest(BaseModel):
    """
    Request body schema for creating a new Chore.

    Inputs:
        name: Name of the Chore.
        description: Description of the Chore.
        due_date: Datetime string representing when the Chore is due.
        assignee_id: Optional unique identifier of the User assigned to the Chore.

    Output:
        JSON body representing a Chore creation request.
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

    Inputs:
        status: Optional new status of the Chore.
        assignee_id: Optional new assignee user ID. Use null to unassign.

    Output:
        JSON body representing a Chore update request.
    """
    status: Union[str, None] = None
    assignee_id: Union[int, None] = None

class ChoreDeleteRequest(BaseModel):
    """
    Request body schema for deleting a Chore.

    Inputs:
        choreid: Unique identifier of the Chore to delete.

    Output:
        JSON body representing a Chore deletion request.
    """
    choreid: int


class ChoreResponse(BaseModel):
    """
    Response schema returned for Chore-related API requests.

    Outputs:
        choreid: Unique identifier of the Chore.
        name: Name of the Chore.
        description: Description of the Chore.
        request_date: Unix timestamp representing when the Chore was requested.
        due_date: Unix timestamp representing when the Chore is due.
        assignee: Full name of the assignee, or null if unassigned.
        status: Current status of the Chore.
    """
    choreid: int = None
    name: str
    description: str
    request_date: Union[int, None] = None
    due_date: Union[int, None] = None
    assignee: Union[str, None] = None
    status: Union[str, None] = None

CHORE_TABLE_NAME = "chores"

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
    status = Status.IN_PROGRESS.value if data[Chore_Col_Name.assignee] else Status.UNASSIGNED.value

    return ChoreCreateRequest(
        householdid=data[Chore_Col_Name.householdid],
        name=data[Chore_Col_Name.cname],
        description=data[Chore_Col_Name.description],
        request_date=datetime.now().isoformat(),
        due_date=data[Chore_Col_Name.due_date],
        requester_id=data[Chore_Col_Name.requester],
        assignee_id=data[Chore_Col_Name.assignee],
        status=status
    )

def create_ChoreUpdateRequest(data: dict) -> ChoreUpdateRequest:
    # raises things add comment later
    status = data[Chore_Col_Name.status]
    assignee = data[Chore_Col_Name.assignee]
    if is_valid_status(status=status, assignee=assignee):
        return ChoreUpdateRequest(
            status=status,
            assignee_id=assignee
        )
    else:
        return None

def create_ChoreDeleteRequest(data: dict) -> ChoreDeleteRequest:
    return ChoreDeleteRequest(
        choreid=data[Chore_Col_Name.choreid]
    )

def create_ChoreResponse(data: dict, assignee: Union[UserResponse, None] = None) -> ChoreResponse:
    assignee_name = get_full_name(assignee) if assignee else None

    return ChoreResponse(
        choreid=data[Chore_Col_Name.choreid],
        name=data[Chore_Col_Name.cname],
        description=data[Chore_Col_Name.description],
        request_date=data[Chore_Col_Name.request_date],
        due_date=data[Chore_Col_Name.due_date],
        assignee=assignee_name,
        status=data[Chore_Col_Name.status])

def is_valid_status(status: str, assignee: Union[int, None] = None) -> bool:
    if not status.upper() in Status.__members__:
        raise ValueError("Not a valid Status Type.")
    
    if assignee and status.upper() == Status.UNASSIGNED.name:
        raise ValueError("Can not be given the status unassigned if assignee exists.")
    
    if not assignee and status.upper() == Status.IN_PROGRESS.name:
        raise ValueError("Can not be given the status in progress if assignee doesn't exist.")
    
    return True


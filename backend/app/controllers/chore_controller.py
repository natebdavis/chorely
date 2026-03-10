from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

"""
Module for managing Chore Controller operations.
Handles HTTP requests related to Chores and exposes API endpoints
for creating, retrieving, and deleting chores.
Contributers: Edmund Krajewski
"""

router = APIRouter(prefix="/chores", tags=["chores"])


class ChoreStatus(str, Enum):
    """Enumeration representing the current status of a Chore."""
    UNASSIGNED = "UNASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETE = "COMPLETE"
    CANCELLED = "CANCELLED"


class ChoreCreateRequest(BaseModel):
    """
    Request body schema for creating a new Chore.

    Inputs:
        name: Name/title of the chore.
        description: Optional detailed description of the chore.
        assigned_to: Optional username of the user assigned to the chore.

    Output:
        JSON body representing the chore creation request.
    """
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=3000)
    assigned_to: Optional[str] = None


class ChoreResponse(BaseModel):
    """
    Response schema returned for Chore-related API requests.

    Outputs:
        id: Unique identifier for the chore.
        name: Name of the chore.
        description: Description of the chore.
        assigned_to: Username of the user assigned to the chore.
        status: Current status of the chore.
    """
    id: int
    name: str
    description: str
    assigned_to: Optional[str]
    status: ChoreStatus


"""
Temporary in-memory storage for Chores.

This acts as a placeholder for persistent database storage
until database integration is implemented.
"""
fake_chores: list[ChoreResponse] = []
next_id = 1


@router.get("", response_model=list[ChoreResponse])
def get_chores():
    """
    Retrieve all chores currently stored.

    Inputs:
        None

    Outputs:
        List of all Chore objects currently in the system.
    """
    return fake_chores


@router.post("", response_model=ChoreResponse, status_code=status.HTTP_201_CREATED)
def create_chore(payload: ChoreCreateRequest):
    """
    Create a new Chore.

    Inputs:
        request: ChoreCreateRequest containing the chore name,
                 description, and optional assignee.

    Outputs:
        Newly created ChoreResponse object added to the system.
    """
    global next_id

    new_chore = ChoreResponse(
        id=next_id,
        name=payload.name,
        description=payload.description,
        assigned_to=payload.assigned_to,
        status=ChoreStatus.IN_PROGRESS if payload.assigned_to else ChoreStatus.UNASSIGNED,
    )

    fake_chores.append(new_chore)
    next_id += 1
    return new_chore


@router.delete("/{chore_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_chore(chore_id: int):
    """
    Delete a Chore by its ID.

    Inputs:
        chore_id: Integer identifier for the chore to delete.

    Outputs:
        HTTP 204 if the chore is successfully deleted.

    Raises:
        HTTPException(404) if the chore ID does not exist.
    """
    global fake_chores

    for i, chore in enumerate(fake_chores):
        if chore.id == chore_id:
            fake_chores.pop(i)
            return

    raise HTTPException(status_code=404, detail="Chore not found")
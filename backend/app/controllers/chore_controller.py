from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

from app import database

"""
Module for managing Chore Controller operations.
Handles HTTP requests related to Chores and exposes API endpoints
for creating, retrieving, and deleting chores.

Contributers: Edmund Krajewski
"""

router = APIRouter(prefix="/chores", tags=["chores"])


class ChoreCreateRequest(BaseModel):
    """
    Request body schema for creating a new Chore.

    Inputs:
        householdid: Unique identifier for the Household.
        requester_id: Unique identifier of the User requesting the Chore.
        name: Name of the Chore.
        description: Description of the Chore.
        due_date: Datetime string representing when the Chore is due.
        assignee_id: Optional unique identifier of the User assigned to the Chore.

    Output:
        JSON body representing a Chore creation request.
    """
    householdid: int
    requester_id: int
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=3000)
    due_date: str
    assignee_id: Optional[int] = None


class ChoreResponse(BaseModel):
    """
    Response schema returned for Chore-related API requests.

    Outputs:
        name: Name of the Chore.
        description: Description of the Chore.
        request_date: Unix timestamp representing when the Chore was requested.
        due_date: Unix timestamp representing when the Chore is due.
        assignee: Full name of the assignee, or null if unassigned.
        status: Current status of the Chore.
    """
    name: str
    description: str
    request_date: Optional[int]
    due_date: Optional[int]
    assignee: Optional[str]
    status: str


@router.get("/{householdid}", response_model=list[ChoreResponse])
def get_chores(householdid: int):
    """
    Retrieve all chores for a given household.

    Inputs:
        householdid: Unique identifier for the Household.

    Outputs:
        A list of ChoreResponse objects for the specified Household.

    Raises:
        HTTPException(500) if there is an error retrieving chores.
    """
    try:
        chores = database.get_chores(householdid)

        if not chores:
            return []

        return [ChoreResponse(**c.createBaseModel()) for c in chores]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chores: {str(e)}"
        )


@router.post("", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def create_chore(payload: ChoreCreateRequest):
    """
    Create a new chore.

    Inputs:
        payload: ChoreCreateRequest containing the Chore data.

    Outputs:
        Currently returns a not implemented response.

    Notes:
        Full database integration for chore creation is not complete yet.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Chore creation is scaffolded but not fully integrated with the database yet"
    )


@router.delete("/{chore_id}", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def delete_chore(chore_id: int):
    """
    Delete a chore by ID.

    Inputs:
        chore_id: Unique identifier for the Chore.

    Outputs:
        Currently returns a not implemented response.

    Notes:
        Full database integration for chore deletion is not complete yet.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Chore deletion is scaffolded but not fully integrated with the database yet"
    )
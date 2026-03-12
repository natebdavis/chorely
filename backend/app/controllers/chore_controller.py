from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
import datetime as DT

from app import database
from app.chore import Chore

"""
Module for managing Chore Controller operations.
Handles HTTP requests related to Chores and exposes API endpoints
for creating, retrieving, and deleting chores.

Contributers: Edmund Krajewski, Gilligan Berlinski
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


class ChoreDeleteRequest(BaseModel):
    """
    Request body schema for deleting a Chore.

    Inputs:
        householdid: Unique identifier for the Household.
        choreid: Unique identifier of the Chore to delete.

    Output:
        JSON body representing a Chore deletion request.
    """
    householdid: int
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
    choreid: Optional[int] = None
    name: str
    description: str
    request_date: Optional[int] = None
    due_date: Optional[int] = None
    assignee: Optional[str] = None
    status: Optional[str] = None


@router.get("/{householdid}", response_model=list[ChoreResponse])
def get_household_chores(householdid: int):
    """
    Retrieve all chores for a given household.
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


@router.post("", response_model=ChoreResponse, status_code=status.HTTP_201_CREATED)
def create_chore(payload: ChoreCreateRequest):
    """
    Create a new chore.

    Inputs:
        payload: ChoreCreateRequest containing the Chore data.

    Outputs:
        The newly created ChoreResponse object.

    Raises:
        HTTPException(404) if requester or assignee does not exist.
        HTTPException(400) if due_date format is invalid.
        HTTPException(500) if database insertion fails.
    """
    try:
        requester = database.get_user(payload.requester_id)
        if not requester:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Requester not found"
            )

        assignee = None
        if payload.assignee_id is not None:
            assignee = database.get_user(payload.assignee_id)
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assignee not found"
                )

        try:
            due_date = DT.datetime.fromisoformat(payload.due_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid due_date format. Use ISO format, e.g. 2026-03-20T18:00:00"
            )

        chore = Chore(
            name=payload.name,
            description=payload.description,
            due_date=due_date,
            requester=requester,
            choreid=None,
            assignee=assignee,
            request_date=None,
        )

        database.add_chore(payload.householdid, chore)

        return ChoreResponse(**chore.createBaseModel())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chore: {str(e)}"
        )


@router.delete("", status_code=status.HTTP_200_OK)
def delete_chore(payload: ChoreDeleteRequest):
    """
    Delete a chore by household ID and chore ID.

    Inputs:
        payload: ChoreDeleteRequest containing the household ID and chore ID.

    Outputs:
        Success message if the chore is deleted.

    Raises:
        HTTPException(404) if no matching chore is found.
        HTTPException(500) if deletion fails.
    """
    try:
        deleted = database.remove_chore(payload.householdid, payload.choreid)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chore not found"
            )

        return {"message": "Chore deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chore: {str(e)}"
        )
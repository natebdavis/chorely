from fastapi import APIRouter, HTTPException, status, Depends
import datetime as DT
from app.database import get_current_user
from app.user import UserResponse
from app import database
from app.chore import Chore, ChoreCreateRequest, ChoreDeleteRequest, ChoreResponse, ChoreUpdateRequest

"""
Module for managing Chore Controller operations.
Handles HTTP requests related to Chores and exposes API endpoints
for creating, retrieving, and deleting chores.

Contributers: Edmund Krajewski, Gilligan Berlinski
"""

router = APIRouter(prefix="/chores", tags=["chores"])

@router.patch("/{choreid}", response_model=ChoreResponse)
def update_chore(choreid: int, payload: ChoreUpdateRequest):
    """
    Update a chore's status and/or assignee.

    Inputs:
        choreid: Unique identifier of the Chore.
        payload: ChoreUpdateRequest containing updated fields.

    Outputs:
        Updated ChoreResponse object.

    Raises:
        HTTPException(400) if status is invalid.
        HTTPException(404) if assignee is not found or chore is not found.
        HTTPException(500) if update fails.
    """
    try:
        valid_statuses = {"UNASSIGNED", "IN_PROGRESS", "COMPLETE"}

        if payload.status is not None and payload.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status value"
            )

        if payload.assignee_id is not None:
            assignee = database.get_user(payload.assignee_id)
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assignee not found"
                )

        updated = database.update_chore(
            household=payload.householdid,
            choreid=choreid,
            status=payload.status,
            assignee_id=payload.assignee_id,
        )

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chore not found"
            )

        chores = database.get_chores(payload.householdid)
        if not chores:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Updated chore not found"
            )

        for chore in chores:
            if chore.choreid == choreid:
                return ChoreResponse(**chore.createBaseModel())

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Updated chore not found"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update chore: {str(e)}"
        )

@router.get("/{householdid}", response_model=list[ChoreResponse])
def get_household_chores(householdid: int, current_user: UserResponse = Depends(get_current_user)):
    """
    Retrieve all chores for a given household.
    """
    try:
        if current_user["householdid"] != householdid:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not authorized to view chores for this household"
            )

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
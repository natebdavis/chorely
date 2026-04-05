from fastapi import APIRouter, HTTPException, status, Depends
import datetime as DT

from app.database import (
    add_chore as db_add_chore,
    get_chores as db_get_chores,
    get_current_user,
    get_user as db_get_user,
    get_chore as db_get_chore,
    remove_chore as db_remove_chore,
    update_chore as db_update_chore,
    edit_chore as db_edit_chore
)
from app.user import UserResponse
from app.chore import (
    ChoreCreateInput,
    ChoreCreateRequest,
    ChoreDeleteRequest,
    ChoreEditRequest,
    ChoreResponse,
    ChoreUpdateRequest,
    Priority,
    Location,
    Type
)

"""
Module for managing Chore Controller operations.
Handles HTTP requests related to Chores and exposes API endpoints
for creating, retrieving, updating, and deleting chores.

Contributers: Edmund Krajewski, Gilligan Berlinski
"""

router = APIRouter(prefix="/chores", tags=["chores"])

@router.patch("/edit/{choreid}", response_model=ChoreResponse)
def edit_chore_route(
    choreid: int,
    payload: ChoreEditRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Edit an existing chore's details (name, description, due date, priority, type, location).
    """
    try:
        chore = db_get_chore(choreid)

        if not chore:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chore not found",
            )

        if chore.householdid != current_user.householdid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chore not found in user's household",
            )
        
        if current_user.userid != chore.requester_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the requester can edit this chore",
            )
        
        # Validate priority, type, and location if they are provided
        if payload.priority is not None and payload.priority not in Priority.__members__:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid priority value",
            )
        if payload.ctype is not None and payload.ctype not in Type.__members__:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid type value",
            )
        if payload.location is not None and payload.location not in Location.__members__:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid location value",
            )

        updated = db_edit_chore(chore=payload, choreid=choreid)

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update chore",
            )

        return updated

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to edit chore: {str(e)}",
        )
    
@router.patch("/{choreid}", response_model=ChoreResponse)
def update_chore_route(
    choreid: int,
    payload: ChoreUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Update a chore's status and/or assignee.
    """
    try:
        valid_statuses = {"UNASSIGNED", "IN_PROGRESS", "COMPLETE"}

        if payload.status is not None and payload.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status value",
            )
        
        # Validate priority, type, and location if they are provided
        if payload.priority is not None and payload.priority not in Priority.__members__:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid priority value",
            )
        if payload.ctype is not None and payload.ctype not in Type.__members__:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid type value",
            )
        if payload.location is not None and payload.location not in Location.__members__:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid location value",
            )

        assignee = None
        if payload.assignee_id is not None:
            assignee = db_get_user(userid=payload.assignee_id)
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assignee not found",
                )

            if assignee.householdid != current_user.householdid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Assignee must be in the same household",
                )

        if payload.assignee_id is None and payload.status == "IN_PROGRESS":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status cannot be set to IN_PROGRESS without an assignee",
            )

        if payload.assignee_id is not None and payload.status == "UNASSIGNED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status cannot be set to UNASSIGNED with an assignee",
            )

        updated = db_update_chore(
            householdid=current_user.householdid,
            choreid=choreid,
            status=payload.status,
            assignee_id=payload.assignee_id,
            priority=payload.priority,
            ctype=payload.ctype,
            location=payload.location
        )

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chore not found",
            )

        return updated

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update chore: {str(e)}",
        )


@router.get("/{choreid}", response_model=ChoreResponse)
def get_chore_route(
    choreid: int,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Retrieve a single chore by its ID.
    """
    try:
        chore = db_get_chore(choreid)

        if not chore:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chore not found",
            )

        if chore.householdid != current_user.householdid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chore not found in user's household",
            )

        return chore

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chore: {str(e)}",
        )


@router.get("", response_model=list[ChoreResponse])
def get_household_chores(
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Retrieve all chores for the current user's household.
    """
    try:
        householdid = current_user.householdid

        if not householdid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User has not joined a household",
            )

        chores = db_get_chores(householdid)

        return chores or []

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chores: {str(e)}",
        )


@router.post("", response_model=ChoreResponse, status_code=status.HTTP_201_CREATED)
def create_chore(
    payload: ChoreCreateInput,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Create a new chore.
    """
    try:
        householdid = current_user.householdid

        if not householdid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must belong to a household to create chores",
            )

        if payload.assignee_id is not None:
            assignee = db_get_user(userid=payload.assignee_id)
            if not assignee:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Assignee not found",
                )

            if assignee.householdid != householdid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Assignee must be in the same household as the requester",
                )
            
        # Validate priority, type, and location if they are provided
        if payload.priority is not None and payload.priority not in Priority.__members__:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid priority value",
            )
        if payload.ctype is not None and payload.ctype not in Type.__members__:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid type value",
            )
        if payload.location is not None and payload.location not in Location.__members__:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid location value",
            )
        
        try:
            due_date = DT.datetime.fromisoformat(payload.due_date)
            current_time = DT.datetime.now()

            if due_date < current_time:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Due date cannot be in the past",
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid due_date format. Use ISO format, e.g. 2026-03-20T18:00:00",
            )

        final_payload = ChoreCreateRequest(
            householdid=householdid,
            name=payload.name,
            description=payload.description,
            request_date=DT.datetime.now().isoformat(),
            due_date=payload.due_date,
            requester_id=current_user.userid,
            assignee_id=payload.assignee_id,
            status="IN_PROGRESS" if payload.assignee_id is not None else "UNASSIGNED",
            priority=payload.priority,
            ctype=payload.ctype,
            location=payload.location
        )

        created = db_add_chore(final_payload)

        if not created:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create chore",
            )

        return created

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chore: {str(e)}",
        )


@router.delete("", status_code=status.HTTP_200_OK)
def delete_chore(
    payload: ChoreDeleteRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Delete a chore by chore ID.
    """
    try:
        deleted = db_remove_chore(current_user.householdid, payload.choreid)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chore not found",
            )

        return {"message": "Chore deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete chore: {str(e)}",
        )
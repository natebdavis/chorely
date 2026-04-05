from fastapi import APIRouter, HTTPException, status, Depends
import datetime as DT

from app.database import (
    add_chore as db_add_chore,
    add_notification as db_add_notification,
    get_chores as db_get_chores,
    get_current_user,
    get_user as db_get_user,
    get_chore as db_get_chore,
    remove_chore as db_remove_chore,
    update_chore as db_update_chore,
)
from app.user import UserResponse, get_full_name
from app.chore import (
    ChoreCreateInput,
    ChoreCreateRequest,
    ChoreDeleteRequest,
    ChoreResponse,
    ChoreUpdateRequest,
    Status,
)
from app.notification import NotificationCreateRequest, NotificationType

"""
Module for managing Chore Controller operations.
Handles HTTP requests related to Chores and exposes API endpoints
for creating, retrieving, updating, and deleting chores.

Contributers: Edmund Krajewski, Gilligan Berlinski
"""

router = APIRouter(prefix="/chores", tags=["chores"])


@router.patch("/{choreid}", response_model=ChoreResponse)
def update_chore_route(
    choreid: int,
    payload: ChoreUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Update a chore's status and/or assignee using PATCH semantics.
    """
    try:
        existing = db_get_chore(choreid)

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chore not found",
            )

        if existing.householdid != current_user.householdid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chore not found in user's household",
            )

        fields_set = getattr(payload, "model_fields_set", set())
        status_provided = "status" in fields_set
        assignee_provided = "assignee_id" in fields_set

        if not status_provided and not assignee_provided:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No chore fields provided for update",
            )

        final_status = existing.status
        if status_provided and payload.status is not None:
            final_status = payload.status.upper()

        final_assignee = existing.assignee_id
        if assignee_provided:
            final_assignee = payload.assignee_id

        if assignee_provided and not status_provided:
            if payload.assignee_id is None:
                final_status = Status.UNASSIGNED.name
            elif existing.assignee_id is None and existing.status == Status.UNASSIGNED.name:
                final_status = Status.IN_PROGRESS.name

        if assignee_provided and payload.assignee_id is not None:
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

        valid_statuses = {s.name for s in Status}

        if final_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status value",
            )

        if final_status == Status.IN_PROGRESS.name and final_assignee is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status cannot be IN_PROGRESS without an assignee",
            )

        if final_status == Status.UNASSIGNED.name and final_assignee is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Status cannot be UNASSIGNED with an assignee",
            )

        resolved_status_provided = status_provided or (final_status != existing.status)

        updated = db_update_chore(
            householdid=current_user.householdid,
            choreid=choreid,
            status=final_status if resolved_status_provided else None,
            assignee_id=payload.assignee_id if assignee_provided else None,
            status_provided=resolved_status_provided,
            assignee_provided=assignee_provided,
        )

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chore not found",
            )

        now = DT.datetime.now().isoformat()

        if updated.assignee_id != existing.assignee_id and updated.assignee_id is not None:
            if updated.assignee_id != current_user.userid:
                db_add_notification(
                    NotificationCreateRequest(
                        userid=updated.assignee_id,
                        type=NotificationType.CHORE_ASSIGNED.value,
                        title="Chore Assigned",
                        message=f"{get_full_name(current_user)} assigned you the chore '{updated.name}'",
                        reference_id=updated.choreid,
                        time=now,
                        is_read=False,
                    )
                )

        if existing.status != Status.COMPLETE.name and updated.status == Status.COMPLETE.name:
            if updated.requester_id is not None and updated.requester_id != current_user.userid:
                db_add_notification(
                    NotificationCreateRequest(
                        userid=updated.requester_id,
                        type=NotificationType.CHORE_COMPLETED.value,
                        title="Chore Completed",
                        message=f"{get_full_name(current_user)} completed the chore '{updated.name}'",
                        reference_id=updated.choreid,
                        time=now,
                        is_read=False,
                    )
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

        if householdid is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User has not joined a household",
            )

        return list(db_get_chores(householdid))

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

        if householdid is None:
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
            status=Status.IN_PROGRESS.name if payload.assignee_id is not None else Status.UNASSIGNED.name,
        )

        created = db_add_chore(final_payload)

        if not created:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create chore",
            )

        if created.assignee_id is not None and created.assignee_id != current_user.userid:
            db_add_notification(
                NotificationCreateRequest(
                    userid=created.assignee_id,
                    type=NotificationType.CHORE_ASSIGNED.value,
                    title="Chore Assigned",
                    message=f"{get_full_name(current_user)} assigned you the chore '{created.name}'",
                    reference_id=created.choreid,
                    time=DT.datetime.now().isoformat(),
                    is_read=False,
                )
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
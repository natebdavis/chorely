"""
Module for managing Chore Controller operations.
Handles HTTP requests related to Chores and exposes API endpoints
for creating, retrieving, updating, and deleting chores.

Contributers: Edmund Krajewski, Gilligan Berlinski
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
import datetime as DT

from app.database import (
    add_chore as db_add_chore,
    add_notification as db_add_notification,
    get_chores as db_get_chores,
    get_chores_in_range as db_get_chores_in_range,
    get_assigned_chores_in_range as db_get_assigned_chores_in_range,
    get_current_user,
    get_user as db_get_user,
    get_chore as db_get_chore,
    remove_chore as db_remove_chore,
    update_chore as db_update_chore,
    edit_chore as db_edit_chore,
    get_filtered_chores as db_get_filtered_chores,
)

from app.user import UserResponse, get_full_name
from app.chore import (
    ChoreCreateInput,
    ChoreCreateRequest,
    ChoreDeleteRequest,
    ChoreEditRequest,
    ChoreResponse,
    ChoreUpdateRequest,
    ChoreSearchRequest,
    ChoreRangeResponse,
    Priority,
    Location,
    Type,
    Status,
)

from app.notification import NotificationCreateRequest, NotificationType
from app.utils import Weekday, DateFilter
from app.chore_generation import (
    generate_due_chores_for_household_in_range,
    build_chore_range_response,
)

router = APIRouter(prefix="/chores", tags=["chores"])
""" API router for chore-related endpoints. All routes defined in this module"""


@router.patch("/edit/{choreid}", response_model=ChoreResponse)
def edit_chore_route(
    choreid: int,
    payload: ChoreEditRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Edit an existing chore's details (name, description, due date, priority, type, location).

    Raises:
    - HTTPException 400: If the user is not part of a household, if the chore fields are invalid, or if the due date is in the past.
    - HTTPException 403: If the user is not the requester of the chore.
    - HTTPException 404: If the chore is not found or not in the user's household.
    - HTTPException 500: If there is an error updating the chore.
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
    Update a chore's status and/or assignee using PATCH semantics.

    Raises:
    - HTTPException 400: If the user is not part of a household, if the status/assignee values are invalid,
            if the status/assignee combination is invalid, or if the due date is in the past.
    - HTTPException 404: If the chore is not found or not in the user's household,
            or if the new assignee is not found.
    - HTTPException 500: If there is an error updating the chore.
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
            priority=payload.priority,
            ctype=payload.ctype,
            location=payload.location,
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


@router.get("/assigned/range", response_model=ChoreRangeResponse)
def get_assigned_chores_range(
    start_date: str = Query(..., description="Inclusive ISO date or datetime lower bound"),
    end_date: str = Query(..., description="Inclusive ISO date or datetime upper bound"),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Retrieve chores assigned to the current user in a specific date range.

    This endpoint still generates household recurring chores for the range first,
    then filters the returned chores down to only those assigned to the user.

    Raises:
    - HTTPException 400: If the user is not part of a household, or if the date formats are invalid, or if end_date is before start_date.
    - HTTPException 404: If the user's household is not found.
    - HTTPException 500: If there is an error retrieving the chores.
    """
    try:
        householdid = current_user.householdid

        if householdid is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User has not joined a household",
            )

        try:
            range_start = DT.datetime.fromisoformat(start_date)
            range_end = DT.datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format, e.g. 2026-04-01 or 2026-04-01T00:00:00",
            )

        if range_end < range_start:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="end_date must be greater than or equal to start_date",
            )

        generate_due_chores_for_household_in_range(
            householdid=householdid,
            range_start=range_start,
            range_end=range_end,
        )

        chores = list(
            db_get_assigned_chores_in_range(
                householdid=householdid,
                userid=current_user.userid,
                start_date=range_start.isoformat(),
                end_date=range_end.isoformat(),
            )
        )

        return build_chore_range_response(
            chores=chores,
            range_start=range_start,
            range_end=range_end,
            now=DT.datetime.now(),
            current_user_id=current_user.userid,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve assigned chores in range: {str(e)}",
        )


@router.get("/range", response_model=ChoreRangeResponse)
def get_household_chores_in_range(
    start_date: str = Query(..., description="Inclusive ISO date or datetime lower bound"),
    end_date: str = Query(..., description="Inclusive ISO date or datetime upper bound"),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Retrieve chores for the current user's household in a specific date range.

    This endpoint also generates any missing recurring chores for the requested
    range before returning the response.

    The response is optimized for mobile calendar/day caching and includes:
    - chores grouped by date
    - per-date calendar metadata such as overdue markers

    Raises:
    - HTTPException 400: If the user is not part of a household, or if the date formats are invalid, or if end_date is before start_date.
    - HTTPException 404: If the user's household is not found.
    - HTTPException 500: If there is an error retrieving the chores.
    """
    try:
        householdid = current_user.householdid

        if householdid is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User has not joined a household",
            )

        try:
            range_start = DT.datetime.fromisoformat(start_date)
            range_end = DT.datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format, e.g. 2026-04-01 or 2026-04-01T00:00:00",
            )

        if range_end < range_start:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="end_date must be greater than or equal to start_date",
            )

        generate_due_chores_for_household_in_range(
            householdid=householdid,
            range_start=range_start,
            range_end=range_end,
        )

        chores = list(
            db_get_chores_in_range(
                householdid=householdid,
                start_date=range_start.isoformat(),
                end_date=range_end.isoformat(),
            )
        )

        return build_chore_range_response(
            chores=chores,
            range_start=range_start,
            range_end=range_end,
            now=DT.datetime.now(),
            current_user_id=current_user.userid,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve chores in range: {str(e)}",
        )


@router.get("/{choreid}", response_model=ChoreResponse)
def get_chore_route(
    choreid: int,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Retrieve a single chore by its ID.

    Raises:
    - HTTPException 400: If the user is not part of a household.
    - HTTPException 404: If the chore is not found or not in the user's household.
    - HTTPException 500: If there is an error retrieving the chore.
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

    Legacy endpoint retained for compatibility.

    Raises:
    - HTTPException 400: If the user is not part of a household.
    - HTTPException 404: If the user has not joined a household.
    - HTTPException 500: If there is an error retrieving the chores.
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
    
@router.post("/filtered", response_model=list[ChoreResponse])
def get_filtered_chores(
    request: ChoreSearchRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Retrieve chores for the current user's household filtered by various criteria.

    Raises:
    - HTTPException 400: If the user is not part of a household, or if any of the filter values are invalid.
    - HTTPException 404: If the user is not joined a household.
    - HTTPException 500: If there is an error retrieving the chores.
    """
    try:
        householdid = current_user.householdid

        if householdid is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User has not joined a household",
            )
        

        if request.priority is not None and request.priority not in Priority.__members__:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid priority value",
            )
        if request.ctype is not None and request.ctype not in Type.__members__:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid type value",
            )
        if request.location is not None and request.location not in Location.__members__:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid location value",
            )
        if request.status is not None and request.status not in Status.__members__:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status value",
            )
        if request.weekday is not None and (request.weekday < Weekday.MONDAY or request.weekday > Weekday.SUNDAY):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="weekday must be between 0 (Mon) and 6 (Sun)",
            )
        if request.date_filter is not None and request.date_filter not in DateFilter.__members__:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_filter value",
            )

        return list(db_get_filtered_chores(householdid=householdid, 
                                           status=Status[request.status] if request.status else None,
                                           priority=Priority[request.priority] if request.priority else None,
                                           ctype=Type[request.ctype] if request.ctype else None,
                                           location=Location[request.location] if request.location else None,
                                           weekday=Weekday(request.weekday) if request.weekday is not None else None,
                                           date_filter=DateFilter[request.date_filter] if request.date_filter else None))

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

    Raises:
    - HTTPException 400: If the user is not part of a household, if the chore fields are invalid, or if the due date is in the past.
    - HTTPException 404: If the user is not joined to a household, or if the assignee (if provided) is not found.
    - HTTPException 500: If there is an error creating the chore.
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

            if due_date.tzinfo is not None:
                current_time = DT.datetime.now(due_date.tzinfo)
            else:
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
            template_id=None,
            status=Status.IN_PROGRESS.name if payload.assignee_id is not None else Status.UNASSIGNED.name,
            priority=payload.priority,
            ctype=payload.ctype,
            location=payload.location,
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

    Raises:
    - HTTPException 400: If the user is not part of a household, or if the chore ID is invalid.
    - HTTPException 404: If the chore is not found or not in the user's household.
    - HTTPException 500: If there is an error deleting the chore.
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
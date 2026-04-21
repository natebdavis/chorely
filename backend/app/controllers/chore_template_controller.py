from fastapi import APIRouter, HTTPException, status, Depends

from app.database import (
    add_chore_template as db_add_chore_template,
    get_chore_template as db_get_chore_template,
    get_chore_templates as db_get_chore_templates,
    update_chore_template as db_update_chore_template,
    deactivate_chore_template as db_deactivate_chore_template,
    get_current_user,
    get_user as db_get_user,
)
from app.user import UserResponse
from app.chore_template import (
    ChoreTemplateCreateInput,
    ChoreTemplateCreateRequest,
    ChoreTemplateResponse,
    ChoreTemplateUpdateRequest,
    RepeatType,
    TimeBucket,
)
from app.chore import Priority, Location, Type

"""
Module for managing Chore Template Controller operations.

Contributors: Edmund Krajewski
"""

router = APIRouter(prefix="/chore-templates", tags=["chore-templates"])


@router.post("", response_model=ChoreTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_chore_template(
    payload: ChoreTemplateCreateInput,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Create a new recurring chore template.
    """
    try:
        householdid = current_user.householdid

        if householdid is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must belong to a household",
            )

        # Validate enums
        if payload.repeat_type not in RepeatType:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid repeat_type",
            )

        if payload.time_bucket not in TimeBucket:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid time_bucket",
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

        # Validate assignee
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
                    detail="Assignee must be in the same household",
                )

        # Build internal request
        template_request = ChoreTemplateCreateRequest(
            householdid=householdid,
            created_by=current_user.userid,
            name=payload.name,
            description=payload.description,
            start_date=payload.start_date,
            end_date=payload.end_date,
            assignee_id=payload.assignee_id,
            time_bucket=payload.time_bucket.value,
            repeat_type=payload.repeat_type.value,
            repeat_interval=payload.repeat_interval,
            repeat_days_of_week=payload.repeat_days_of_week,
            repeat_day_of_month=payload.repeat_day_of_month,
            is_active=True,
            last_generated_at=None,
            priority=payload.priority,
            ctype=payload.ctype,
            location=payload.location,
        )

        created = db_add_chore_template(template_request)

        if not created:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create chore template",
            )

        return created

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create chore template: {str(e)}",
        )


@router.get("", response_model=list[ChoreTemplateResponse])
def get_templates(
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Get all recurring chore templates for the current household.
    """
    try:
        householdid = current_user.householdid

        if householdid is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User has not joined a household",
            )

        return list(db_get_chore_templates(householdid=householdid))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve templates: {str(e)}",
        )


@router.get("/{templateid}", response_model=ChoreTemplateResponse)
def get_template(
    templateid: int,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Get a single recurring chore template.
    """
    try:
        template = db_get_chore_template(templateid)

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found",
            )

        if template.householdid != current_user.householdid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not in user's household",
            )

        return template

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve template: {str(e)}",
        )


@router.patch("/{templateid}", response_model=ChoreTemplateResponse)
def update_template(
    templateid: int,
    payload: ChoreTemplateUpdateRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Update an existing recurring chore template.
    """
    try:
        existing = db_get_chore_template(templateid)

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found",
            )

        if existing.householdid != current_user.householdid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not in user's household",
            )

        updated = db_update_chore_template(templateid, payload)

        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update template",
            )

        return updated

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update template: {str(e)}",
        )


@router.delete("/{templateid}", response_model=ChoreTemplateResponse)
def deactivate_template(
    templateid: int,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Deactivate a recurring chore template.
    """
    try:
        existing = db_get_chore_template(templateid)

        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found",
            )

        if existing.householdid != current_user.householdid:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not in user's household",
            )

        deactivated = db_deactivate_chore_template(templateid)

        if not deactivated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deactivate template",
            )

        return deactivated

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate template: {str(e)}",
        )
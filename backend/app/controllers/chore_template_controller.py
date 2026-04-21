from fastapi import APIRouter, HTTPException

from app.chore_template import (
    ChoreTemplateCreateInput,
    ChoreTemplateCreateRequest,
)
from app.database import (
    add_chore_template,
    get_chore_templates,
    get_chore_template,
    update_chore_template,
    deactivate_chore_template,
)

"""
Controller for recurring chore templates.

Contributors: Edmund Krajewski
"""

router = APIRouter(prefix="/chore-templates", tags=["Chore Templates"])


@router.post("/")
def create_chore_template(data: dict):
    """
    Create a new recurring chore template.
    """
    try:
        input_data = ChoreTemplateCreateInput(**data)

        request = ChoreTemplateCreateRequest(
            householdid=data["householdid"],
            created_by=data["created_by"],
            name=input_data.name,
            description=input_data.description,
            start_date=input_data.start_date,
            end_date=input_data.end_date,
            assignee_id=input_data.assignee_id,
            time_bucket=input_data.time_bucket.value,
            repeat_type=input_data.repeat_type.value,
            repeat_interval=input_data.repeat_interval,
            repeat_days_of_week=input_data.repeat_days_of_week,
            repeat_day_of_month=input_data.repeat_day_of_month,
            preview_days=input_data.preview_days,
            priority=input_data.priority,
            ctype=input_data.ctype,
            location=input_data.location,
        )

        created = add_chore_template(request)

        if created is None:
            raise HTTPException(status_code=400, detail="Failed to create chore template")

        return created

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{householdid}")
def get_templates_for_household(householdid: int):
    """
    Get all recurring chore templates for a household.
    """
    try:
        templates = get_chore_templates(householdid=householdid)
        return list(templates)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/template/{templateid}")
def get_single_template(templateid: int):
    """
    Get a single recurring chore template.
    """
    template = get_chore_template(templateid)

    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.patch("/{templateid}")
def update_template(templateid: int, data: dict):
    """
    Update an existing recurring chore template.
    """
    try:
        updated = update_chore_template(templateid, data)

        if updated is None:
            raise HTTPException(status_code=404, detail="Template not found or update failed")

        return updated

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{templateid}")
def deactivate_template(templateid: int):
    """
    Deactivate a recurring chore template.
    """
    template = deactivate_chore_template(templateid)

    if template is None:
        raise HTTPException(status_code=404, detail="Template not found")

    return {"message": "Template deactivated successfully"}
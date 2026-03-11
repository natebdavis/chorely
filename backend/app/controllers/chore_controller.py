from fastapi import APIRouter, HTTPException, status

from app.chore import Chore, ChoreCreateRequest, ChoreResponse, Status
import app.database as DB
from app.user import User

"""
Module for managing Chore Controller operations.
Handles HTTP requests related to Chores and exposes API endpoints
for creating, retrieving, and deleting chores.
Contributers: Edmund Krajewski, Gilligan Berlinski
"""

router = APIRouter(prefix="/chores", tags=["chores"])

"""
Temporary in-memory storage for Chores.

This acts as a placeholder for persistent database storage
until database integration is implemented.
"""
next_id = 1
fake_chores: list[ChoreResponse] = []
householdid = 1


"""
Temporary in-memory storage for Chores and Users.

Given a householdid pulls all users and chores currently in household
"""
users: list[User] = DB.get_users(householdid=householdid)
chores: list[Chore] = DB.get_chores(householdid=householdid, users=users)


@router.get("", response_model=list[ChoreResponse])
def get_chores():
    """
    Retrieve all chores currently stored.

    Inputs:
        None

    Outputs:
        List of all Chore objects currently in the system.
    """
    global chores

    return [c.get_chore_response_model for c in chores]

# Don't need to keep a global variable of id, database automatically assigns ids
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
        status=Status.IN_PROGRESS.name if payload.assigned_to else Status.UNASSIGNED.name,
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
    global chores

    for i, c in enumerate(chores):
        if c.choreid == chore_id:
            chores.pop(i)
            # Need to add section where database is updated during this action
            return

    raise HTTPException(status_code=404, detail="Chore not found")
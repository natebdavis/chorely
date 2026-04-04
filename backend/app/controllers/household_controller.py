from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.household import (
    HouseholdResponse,
    HouseholdJoinRequest,
    HouseholdLeaveRequest,
)
from app.database import (
    get_household_member_count,
    get_current_user,
    get_householdid,
    join_household,
    create_household_db,
    get_users,
    leave_household,
    get_user,
)
from app.user import UserResponse

"""
Module for managing Household Controller operations.
Handles HTTP requests related to Households and exposes API endpoints
for creating and retrieving household information.

Contributors: Edmund Krajewski, Gilligan Berlinski
"""

router = APIRouter(tags=["households"], prefix="/households")


@router.get("/members", response_model=List[UserResponse])
def get_household_users(current_user: UserResponse = Depends(get_current_user)):
    """
    Retrieve all users belonging to the current user's household.
    """
    householdid = current_user.householdid

    if householdid is None:
        raise HTTPException(
            status_code=404,
            detail="User has not joined a household",
        )

    users = get_users(householdid)

    if not users:
        raise HTTPException(
            status_code=404,
            detail="No users in household found",
        )

    return users


@router.get("", response_model=HouseholdResponse)
def get_household(current_user: UserResponse = Depends(get_current_user)):
    """
    Retrieve household information for the current user.
    """
    householdid = current_user.householdid

    if householdid is None:
        raise HTTPException(
            status_code=404,
            detail="User has not joined a household",
        )

    return HouseholdResponse(
        householdid=householdid,
        member_count=get_household_member_count(householdid),
    )


@router.post("", response_model=HouseholdResponse)
def create_household(current_user: UserResponse = Depends(get_current_user)):
    """
    Create a new household and add the current user as a member.
    """
    householdid = get_householdid(current_user.userid)

    if householdid is not None:
        raise HTTPException(
            status_code=400,
            detail="User is already apart of an existing household.",
        )

    new_household = create_household_db()

    if not new_household:
        raise HTTPException(
            status_code=500,
            detail="Failed to create household",
        )

    joined_user = join_household(current_user.userid, new_household.householdid)

    if not joined_user:
        raise HTTPException(
            status_code=500,
            detail="Failed to add user to newly created household",
        )

    return HouseholdResponse(
        householdid=new_household.householdid,
        member_count=1,
    )


@router.post("/join")
def join_household_route(
    request: HouseholdJoinRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Allow a user to add another user to their household.
    """
    current_householdid = get_householdid(userid=current_user.userid)

    if current_householdid is None:
        raise HTTPException(
            status_code=400,
            detail="User must be a member of a household to add another user to it.",
        )

    member_count = get_household_member_count(current_householdid)
    if member_count >= 10:
        raise HTTPException(
            status_code=400,
            detail="Household has reached maximum member limit",
        )

    user = get_user(userid=request.userid)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user.householdid == current_householdid:
        raise HTTPException(
            status_code=400,
            detail="User already belongs to this household",
        )

    if user.householdid is not None:
        raise HTTPException(
            status_code=400,
            detail="User already belongs to a different household",
        )

    joined_user = join_household(request.userid, current_householdid)

    if not joined_user:
        raise HTTPException(
            status_code=500,
            detail="Failed to add user to household",
        )

    return {"message": "User joined household successfully"}


@router.delete("/leave")
def leave_household_route(
    request: HouseholdLeaveRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Allow a user to leave their current household.
    """
    if current_user.userid != request.userid:
        raise HTTPException(
            status_code=400,
            detail="Unauthorized user attempting to remove another user from household.",
        )

    user = get_user(userid=request.userid)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user.householdid is None:
        raise HTTPException(
            status_code=400,
            detail="User is not part of a household",
        )

    left_user = leave_household(request.userid)

    if not left_user:
        raise HTTPException(
            status_code=500,
            detail="Failed to leave household",
        )

    return {"message": "User left household successfully"}
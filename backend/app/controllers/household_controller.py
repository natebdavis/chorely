from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.household import HouseholdCreateRequest, HouseholdResponse
from app.database import household_exists, get_household_member_count, get_current_user, get_householdid, join_household, create_household_db, get_users
from app.user import UserResponse

from app.database import join_household, leave_household, get_user, get_householdid, get_current_user, get_household_member_count
from app.household import HouseholdJoinRequest, HouseholdLeaveRequest, MembershipResponse

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
    Retrieve all Users belonging to a household.

    Inputs:
        householdid: Identifier of the household.

    Outputs:
        List of UserResponse objects.

    Raises:
        HTTPException(404) if no users exist for that household.
    """

    userid = current_user["userid"]
    householdid = current_user["householdid"]

    if not householdid:
        raise HTTPException(status_code=404, detail="User has not joined a household")

    users = get_users(householdid)

    if not users:
        raise HTTPException(status_code=404, detail="No users in household found")

    return [
        UserResponse(
            userid=u.userid,
            username=u.username,
            fname=u.fname,
            lname=u.lname,
            email=u.email,
            phone_num=u.phone_num,
        )
        for u in users
    ]

@router.get("", response_model=HouseholdResponse)
def get_households(current_user: UserResponse = Depends(get_current_user)):

    userid = current_user["userid"]
    householdid = get_householdid(userid=userid)

    if not householdid:
        raise HTTPException(status_code=404, detail="User has not joined a household")
    
    return HouseholdResponse(
        householdid=householdid,
        member_count=get_household_member_count(householdid),
    )

@router.post("", response_model=HouseholdResponse)
def create_household(current_user: UserResponse = Depends(get_current_user)):

    householdid = get_householdid(current_user["userid"])

    if householdid:
        raise HTTPException(status_code=404, detail="User is already apart of an existing household.")

    new_household = create_household_db()
    householdid = new_household[0]["householdid"]
    join_household(current_user["userid"], householdid)

    return HouseholdResponse(
        householdid=householdid,
        member_count=1,
    )

@router.post("/join")
def create_membership(request: HouseholdJoinRequest, current_user: UserResponse = Depends(get_current_user)):
    """Allow a user to add a user to their household.
    Inputs:
        request: HouseholdJoinRequest containing the userid of the user being added and the householdid of the household they are being added to."""
    
    current_userid = current_user["userid"]
    current_householdid = get_householdid(userid=current_userid)

    if not current_householdid:
        raise HTTPException(status_code=400, detail="User must be a member of the household to add another user to it.")

    member_count = get_household_member_count(current_householdid)
    if member_count >= 10:  # Assuming a maximum of 10 members per household
        raise HTTPException(status_code=400, detail="Household has reached maximum member limit")

    user = get_user(request.userid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.householdid == current_householdid:
        raise HTTPException(status_code=400, detail="User already belongs to this household")
    
    if user.householdid is not None:
        raise HTTPException(status_code=400, detail="User already belongs to a different household")

    join_household(request.userid, current_householdid)
    return {"message": "User joined household successfully"}


@router.delete("/leave")
def delete_membership(request: HouseholdLeaveRequest, current_user: UserResponse = Depends(get_current_user)):
    """Allow a user to leave their current household.
    Inputs:
        request: HouseholdLeaveRequest containing the userid of the user leaving the household."""

    current_userid = current_user["userid"]

    if current_userid != request.userid:
        raise HTTPException(status_code=400, detail="Unauthorized user attempting to remove another user from household.")

    user = get_user(request.userid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.householdid is None:
        raise HTTPException(status_code=400, detail="User is not part of a household")

    leave_household(request.userid)
    return {"message": "User left household successfully"}
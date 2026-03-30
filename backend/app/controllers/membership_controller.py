from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.database import get_household_members, join_household, leave_household, get_user, get_householdid, get_current_user, get_household_member_count
from app.household import HouseholdJoinRequest, HouseholdLeaveRequest, MembershipResponse
from app.user import UserResponse

"""
Module for managing Membership Controller operations.
Handles HTTP requests related to household membership and exposes API endpoints
for adding, removing, and retrieving household members.

Contributors: Edmund Krajewski
"""

router = APIRouter(tags=["memberships"])


@router.get("/households/{householdid}/members", response_model=List[MembershipResponse])
def get_members(householdid: int):
    members = get_household_members(householdid)

    if not members:
        raise HTTPException(status_code=404, detail="No household members found")

    return [
        MembershipResponse(
            userid=u.userid,
            username=u.username,
            fname=u.fname,
            lname=u.lname,
            email=u.email,
            phone_num=u.phone_num,
        )
        for u in members
    ]


@router.post("/memberships")
def create_membership(request: HouseholdJoinRequest, current_user: UserResponse = Depends(get_current_user)):
    """Allow a user to add a user to their household.
    Inputs:
        request: HouseholdJoinRequest containing the userid of the user being added and the householdid of the household they are being added to."""
    
    current_userid = current_user["userid"]
    current_householdid = get_householdid(userid=current_userid)

    if current_householdid and current_householdid != request.householdid:
        raise HTTPException(status_code=400, detail="Unauthorized user attempting to add another user to household.")
    elif not current_householdid:
        raise HTTPException(status_code=400, detail="User must be a member of the household to add another user to it.")

    member_count = get_household_member_count(request.householdid)
    if member_count >= 10:  # Assuming a maximum of 10 members per household
        raise HTTPException(status_code=400, detail="Household has reached maximum member limit")

    user = get_user(request.userid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.householdid == request.householdid:
        raise HTTPException(status_code=400, detail="User already belongs to this household")
    
    if user.householdid is not None and user.householdid != request.householdid:
        raise HTTPException(status_code=400, detail="User already belongs to a different household")

    join_household(request.userid, request.householdid)
    return {"message": "User joined household successfully"}


@router.delete("/memberships")
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
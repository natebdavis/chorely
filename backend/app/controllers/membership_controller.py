from fastapi import APIRouter, HTTPException
from typing import List

from app.database import get_household_members, join_household, leave_household, get_user
from app.household import HouseholdJoinRequest, HouseholdLeaveRequest, MembershipResponse

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
def create_membership(request: HouseholdJoinRequest):
    user = get_user(request.userid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.householdid == request.householdid:
        raise HTTPException(status_code=400, detail="User already belongs to this household")

    join_household(request.userid, request.householdid)
    return {"message": "User joined household successfully"}


@router.delete("/memberships")
def delete_membership(request: HouseholdLeaveRequest):
    user = get_user(request.userid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.householdid is None:
        raise HTTPException(status_code=400, detail="User is not part of a household")

    leave_household(request.userid)
    return {"message": "User left household successfully"}
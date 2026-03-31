from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.household import HouseholdCreateRequest, HouseholdResponse
from app.database import household_exists, get_household_member_count, get_current_user, get_householdid, join_household, create_household_db, get_users
from app.user import UserResponse

"""
Module for managing Household Controller operations.
Handles HTTP requests related to Households and exposes API endpoints
for creating and retrieving household information.

Contributors: Edmund Krajewski, Gilligan Berlinski
"""

router = APIRouter(tags=["households"])

@router.get("/households/members", response_model=List[UserResponse])
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

@router.get("/households/", response_model=HouseholdResponse)
def get_households(current_user: UserResponse = Depends(get_current_user)):

    userid = current_user["userid"]
    householdid = get_householdid(userid=userid)

    if not householdid:
        raise HTTPException(status_code=404, detail="User has not joined a household")
    
    return HouseholdResponse(
        householdid=householdid,
        member_count=get_household_member_count(householdid),
    )

@router.get("/households/{householdid}", response_model=HouseholdResponse)
def get_household(householdid: int):
    if not household_exists(householdid):
        raise HTTPException(status_code=404, detail="Household not found")

    return HouseholdResponse(
        householdid=householdid,
        member_count=get_household_member_count(householdid),
    )


@router.post("/households", response_model=HouseholdResponse)
def create_household(current_user: UserResponse = Depends(get_current_user)):

    new_household = create_household_db()
    householdid = new_household[0]["householdid"]
    join_household(current_user["userid"], householdid)

    return HouseholdResponse(
        householdid=householdid,
        member_count=1,
    )
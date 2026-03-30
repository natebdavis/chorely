from fastapi import APIRouter, HTTPException, Depends

from app.household import HouseholdCreateRequest, HouseholdResponse
from app.database import household_exists, get_household_member_count, get_current_user, get_householdid
from app.user import UserResponse

"""
Module for managing Household Controller operations.
Handles HTTP requests related to Households and exposes API endpoints
for creating and retrieving household information.

Contributors: Edmund Krajewski, Gilligan Berlinski
"""

router = APIRouter(tags=["households"])

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
def create_household(request: HouseholdCreateRequest):
    if household_exists(request.householdid):
        raise HTTPException(status_code=400, detail="Household already exists")

    return HouseholdResponse(
        householdid=request.householdid,
        member_count=0,
    )
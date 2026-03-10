from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

"""
Module for managing Household Controller operations.
Handles HTTP requests related to Households and exposes API endpoints
for creating and retrieving household information.

Contributors: Edmund Krajewski
"""

router = APIRouter(tags=["households"])


class HouseholdCreateRequest(BaseModel):
    """
    Request body schema for creating a new Household.

    Inputs:
        householdid: Unique identifier for the Household.

    Output:
        JSON body representing a Household creation request.
    """
    householdid: int


class HouseholdResponse(BaseModel):
    """
    Response schema returned for Household-related API requests.

    Outputs:
        householdid: Unique identifier for the Household.
        member_count: Number of Users currently in the Household.
    """
    householdid: int
    member_count: int


class TempHousehold(BaseModel):
    """
    Temporary Household schema used for in-memory backend testing.

    Inputs:
        householdid: Unique identifier for the Household.
        member_count: Number of Users currently in the Household.

    Output:
        Temporary Household object for testing storage and retrieval.
    """
    householdid: int
    member_count: int


"""
Temporary in-memory storage for Households.

This acts as a placeholder until persistent database-backed
Household storage is implemented.
"""
fake_households: List[TempHousehold] = [
    TempHousehold(householdid=1, member_count=2),
    TempHousehold(householdid=2, member_count=4),
]


@router.get("/households", response_model=List[HouseholdResponse])
def get_households():
    """
    Retrieve all Households currently stored.

    Inputs:
        None

    Outputs:
        List of all Households currently in the system.
    """
    return [
        HouseholdResponse(
            householdid=household.householdid,
            member_count=household.member_count,
        )
        for household in fake_households
    ]


@router.get("/households/{householdid}", response_model=HouseholdResponse)
def get_household(householdid: int):
    """
    Retrieve a single Household by householdid.

    Inputs:
        householdid: Unique identifier of the Household to retrieve.

    Outputs:
        HouseholdResponse for the requested Household.

    Raises:
        HTTPException(404) if the Household does not exist.
    """
    for household in fake_households:
        if household.householdid == householdid:
            return HouseholdResponse(
                householdid=household.householdid,
                member_count=household.member_count,
            )

    raise HTTPException(status_code=404, detail="Household not found")


@router.post("/households", response_model=HouseholdResponse)
def create_household(request: HouseholdCreateRequest):
    """
    Create a new Household.

    Inputs:
        request: HouseholdCreateRequest containing the new Household ID.

    Outputs:
        HouseholdResponse representing the newly created Household.

    Raises:
        HTTPException(400) if the Household ID already exists.
    """
    for household in fake_households:
        if household.householdid == request.householdid:
            raise HTTPException(status_code=400, detail="Household already exists")

    new_household = TempHousehold(
        householdid=request.householdid,
        member_count=0,
    )

    fake_households.append(new_household)

    return HouseholdResponse(
        householdid=new_household.householdid,
        member_count=new_household.member_count,
    )
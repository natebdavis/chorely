from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

"""
Module for managing Membership Controller operations.
Handles HTTP requests related to household membership and exposes API endpoints
for adding, removing, and retrieving household members.

Contributors: Edmund Krajewski
"""

router = APIRouter(tags=["memberships"])


class MembershipCreateRequest(BaseModel):
    """
    Request body schema for adding a User to a Household.

    Inputs:
        householdid: Unique identifier for the Household.
        userid: Unique identifier for the User.

    Output:
        JSON body representing a membership creation request.
    """
    householdid: int
    userid: int


class MembershipResponse(BaseModel):
    """
    Response schema returned for Membership-related API requests.

    Outputs:
        householdid: Unique identifier for the Household.
        userid: Unique identifier for the User.
    """
    householdid: int
    userid: int


class TempMembership(BaseModel):
    """
    Temporary Membership schema used for in-memory backend testing.

    Inputs:
        householdid: Unique identifier for the Household.
        userid: Unique identifier for the User.

    Output:
        Temporary Membership object for testing storage and retrieval.
    """
    householdid: int
    userid: int


"""
Temporary in-memory storage for Household memberships.

This acts as a placeholder until persistent database-backed
membership storage is implemented.
"""
fake_memberships: List[TempMembership] = [
    TempMembership(householdid=1, userid=1),
    TempMembership(householdid=1, userid=2),
    TempMembership(householdid=2, userid=3),
]


@router.get("/households/{householdid}/members", response_model=List[MembershipResponse])
def get_household_members(householdid: int):
    """
    Retrieve all memberships belonging to a Household.

    Inputs:
        householdid: Unique identifier of the Household.

    Outputs:
        List of MembershipResponse objects for the requested Household.

    Raises:
        HTTPException(404) if no members are found for the Household.
    """
    members = [
        MembershipResponse(
            householdid=membership.householdid,
            userid=membership.userid,
        )
        for membership in fake_memberships
        if membership.householdid == householdid
    ]

    if not members:
        raise HTTPException(status_code=404, detail="No household members found")

    return members


@router.post("/memberships", response_model=MembershipResponse)
def create_membership(request: MembershipCreateRequest):
    """
    Add a User to a Household.

    Inputs:
        request: MembershipCreateRequest containing the Household ID and User ID.

    Outputs:
        MembershipResponse representing the newly created membership.

    Raises:
        HTTPException(400) if the membership already exists.
    """
    for membership in fake_memberships:
        if membership.householdid == request.householdid and membership.userid == request.userid:
            raise HTTPException(status_code=400, detail="Membership already exists")

    new_membership = TempMembership(
        householdid=request.householdid,
        userid=request.userid,
    )

    fake_memberships.append(new_membership)

    return MembershipResponse(
        householdid=new_membership.householdid,
        userid=new_membership.userid,
    )


@router.delete("/memberships/{householdid}/{userid}")
def delete_membership(householdid: int, userid: int):
    """
    Remove a User from a Household.

    Inputs:
        householdid: Unique identifier for the Household.
        userid: Unique identifier for the User.

    Outputs:
        Success message if membership deletion succeeds.

    Raises:
        HTTPException(404) if the membership does not exist.
    """
    for i, membership in enumerate(fake_memberships):
        if membership.householdid == householdid and membership.userid == userid:
            fake_memberships.pop(i)
            return {"message": "Membership deleted successfully"}

    raise HTTPException(status_code=404, detail="Membership not found")
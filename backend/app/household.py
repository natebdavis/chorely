"""
Module for managing a household.
Contributers: Nathaniel Davis, Edmund Krajewski
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel

HOUSEHOLD_TABLE_NAME = "households"
"""Table name for households."""

class Household_Col_Name(Enum):
    householdid = "householdid"
    ownerid = "owner"


class HouseholdCreateRequest(BaseModel):
    """
    Request body schema for creating a new Household.
    """
    householdid: int


class HouseholdInviteRequest(BaseModel):
    """Request body schema for inviting a user to a Household.
    """
    userid: int
    
class HouseholdRemoveMemberRequest(BaseModel):
    """Request body schema for removing a member from a Household."""
    userid: int

class HouseholdTransferOwnershipRequest(BaseModel):
    """
    Request body schema for transferring ownership of a Household.
    """
    new_owner_userid: int

class HouseholdResponse(BaseModel):
    """
    Response schema returned for Household-related API requests.
    """
    householdid: int
    member_count: int


class MembershipResponse(BaseModel):
    """
    Response schema returned for household membership queries.
    """
    userid: int
    username: str
    fname: str
    lname: str
    email: Optional[str] = None
    phone_num: Optional[int] = None
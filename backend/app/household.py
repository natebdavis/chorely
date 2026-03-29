from enum import Enum
from typing import Optional
from pydantic import BaseModel

"""
Module for managing a household.
Contributers: Nathaniel Davis, Edmund Krajewski
"""

class Household_Col_Name(Enum):
    householdid = "householdid"


class HouseholdCreateRequest(BaseModel):
    """
    Request body schema for creating a new Household.
    """
    householdid: int


class HouseholdJoinRequest(BaseModel):
    """
    Request body schema for joining a Household.
    """
    userid: int
    householdid: int


class HouseholdLeaveRequest(BaseModel):
    """
    Request body schema for leaving a Household.
    """
    userid: int


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
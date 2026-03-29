from enum import Enum

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

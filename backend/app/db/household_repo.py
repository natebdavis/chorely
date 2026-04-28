"""
Module for household-related database operations.

Contributors: Edmund Krajewski, Gilligan Berlinski, Nathaniel Davis
"""

from typing import Union

from supabase import Client

from app.db.client import get_client
from app.db.user_repo import get_user, get_users
from app.household import (
    HOUSEHOLD_TABLE_NAME,
    Household_Col_Name,
    HouseholdResponse,
)
from app.household import HOUSEHOLD_TABLE_NAME, Household_Col_Name
from app.user import USER_TABLE_NAME, User_Col_Name, UserResponse, create_UserResponse
from app.chore import CHORE_TABLE_NAME, Chore_Col_Name
from app.invite import INVITE_TABLE_NAME, Invite_Col_Name

first = 0

def get_householdid(
    userid: int,
    client: Union[Client, None] = None,
) -> Union[int, None]:
    """
    Get the householdid of a user given their userid.

    Output:
        The householdid of the user, or None if the user does not belong to a household.
    """
    if client is None:
        client = get_client()

    user = get_user(userid=userid, client=client)
    if user:
        return user.householdid

    return None


def household_exists(
    householdid: int,
    client: Union[Client, None] = None,
) -> bool:
    """
    Check if a household exists.

    Output:
        True if the household exists, False otherwise.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(HOUSEHOLD_TABLE_NAME)
        .select(Household_Col_Name.householdid.value)
        .eq(Household_Col_Name.householdid.value, householdid)
        .limit(1)
        .execute()
    )

    return bool(response.data)


def join_household(
    userid: int,
    householdid: int,
    is_owner: bool = False,
    client: Union[Client, None] = None,
) -> Union[UserResponse, None]:
    """
    Assign a user to a household.

    Output:
        Updated user data if successful, None otherwise.
    """
    if client is None:
        client = get_client()

    if is_owner:
        ownership_response = (
            client
            .table(HOUSEHOLD_TABLE_NAME)
            .update({Household_Col_Name.ownerid.value: userid})
            .eq(Household_Col_Name.householdid.value, householdid)
            .execute()
        )

        if not ownership_response.data:
            return None

    response = (
        client
        .table(USER_TABLE_NAME)
        .update({User_Col_Name.householdid.value: householdid})
        .eq(User_Col_Name.userid.value, userid)
        .execute()
    )

    rows = response.data
    if not rows:
        return None
    
    row = rows[first]

    return create_UserResponse(row)


def leave_household(
    userid: int,
    client: Union[Client, None] = None,
) -> Union[UserResponse, None]:
    """
    Remove a user from their current household by setting householdid to null.
    Deletes the household if no members remain after the user leaves.

    Output:
        Updated user data if successful, None if user is not found.
    """
    if client is None:
        client = get_client()

    user = get_user(userid=userid, client=client)
    if not user:
        return None

    old_householdid = user.householdid

    response = (
        client
        .table(USER_TABLE_NAME)
        .update({User_Col_Name.householdid.value: None})
        .eq(User_Col_Name.userid.value, userid)
        .execute()
    )

    rows = response.data
    if not rows:
        return None

    if old_householdid is not None:
        delete_household_if_empty(old_householdid, client)

    row = rows[first]

    return create_UserResponse(row)


def delete_household_if_empty(
    householdid: int,
    client: Union[Client, None] = None,
) -> bool:
    """
    If no users remain in a household, delete related chores and delete the household.

    Output:
        True if the household was deleted, False if it still has members.
    """
    if client is None:
        client = get_client()

    members = get_users(householdid=householdid, client=client)
    if members:
        return False

    client.table(CHORE_TABLE_NAME).delete().eq(
        Chore_Col_Name.householdid.value, householdid
    ).execute()

    client.table(INVITE_TABLE_NAME).delete().eq(
        Invite_Col_Name.householdid.value, householdid).execute()

    client.table(HOUSEHOLD_TABLE_NAME).delete().eq(
        Household_Col_Name.householdid.value, householdid
    ).execute()

    return True

def get_owner_householdid(userid: int, client: Union[Client, None] = None) -> Union[int, None]:
   """
    Get the householdid of a household owned by the user with the given userid.
    
    Output:
        The householdid of the owned household, or None if no owned household exists.
    """
   if client is None:
    client = get_client()

    response = (
        client
        .table(HOUSEHOLD_TABLE_NAME)
        .select(Household_Col_Name.householdid.value)
        .eq(Household_Col_Name.ownerid.value, userid)
        .execute()
    )

    if not response.data:
        return None
    else:
        return response.data[first][Household_Col_Name.householdid.value]



def get_household_member_count(
    householdid: int,
    client: Union[Client, None] = None,
) -> int:
    """
    Return the number of users in a household.

    Output:
        Member count for the household. Returns 0 if there are no members.
    """
    if client is None:
        client = get_client()

    members = get_users(householdid=householdid, client=client)
    return len(members) if members else 0


def create_household_db(
    client: Union[Client, None] = None,
) -> Union[HouseholdResponse, None]:
    """
    Create a household in the database.

    Output:
        Inserted household returned as HouseholdResponse, or None if insert failed.
    """
    if client is None:
        client = get_client()

    response = client.table(HOUSEHOLD_TABLE_NAME).insert({}).execute()
    rows = response.data

    if not rows:
        return None

    first_row = rows[first]
    householdid = first_row[Household_Col_Name.householdid.value]
    member_count = get_household_member_count(householdid, client)

    return HouseholdResponse(
        householdid=householdid,
        member_count=member_count,
    )

def transfer_household_ownership(
    householdid: int,
    new_owner_userid: int,
    client: Union[Client, None] = None,
) -> bool:
    """
    Transfer ownership of a household to a new owner.

    Output:
        True if transfer was successful, False otherwise.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(HOUSEHOLD_TABLE_NAME)
        .update({Household_Col_Name.ownerid.value: new_owner_userid})
        .eq(Household_Col_Name.householdid.value, householdid)
        .execute()
    )

    return bool(response.data)
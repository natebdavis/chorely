from collections.abc import Iterable
from typing import Union

from supabase import Client

from app.db.client import get_client
from app.user import (
    USER_TABLE_NAME,
    User_Col_Name,
    UserCreateRequest,
    UserResponse,
    create_UserResponse,
)
from app.chore import CHORE_TABLE_NAME, Chore_Col_Name

"""
Module for user-related database operations.

Contributors: Edmund Krajewski, Gilligan Berlinski, Nathaniel Davis
"""

first = 0

def get_user(
    userid: Union[int, None] = None,
    username: Union[str, None] = None,
    client: Union[Client, None] = None,
) -> Union[UserResponse, None]:
    """
    Get a single user given a userid or username.

    Output:
        A UserResponse matching the search, or None if not found.

    Raises:
        ValueError if neither a username nor userid has been provided.
    """
    if client is None:
        client = get_client()

    if userid is not None:
        col_name = User_Col_Name.userid.value
        val = userid
    elif username is not None:
        col_name = User_Col_Name.username.value
        val = username
    else:
        raise ValueError("Must provide either a username or userid to search for user.")

    response = (
        client
        .table(USER_TABLE_NAME)
        .select("*")
        .eq(col_name, val)
        .execute()
    )

    data = response.data
    if not data:
        return None

    return create_UserResponse(data[first])


def get_users(
    householdid: int,
    client: Union[Client, None] = None,
) -> Union[Iterable[UserResponse], None]:
    """
    Get all users in a household.

    Output:
        An iterable of UserResponse objects in the specified household,
        or None if no users are found.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(USER_TABLE_NAME)
        .select("*")
        .eq(User_Col_Name.householdid.value, householdid)
        .execute()
    )

    data = response.data
    if not data:
        return None

    return [create_UserResponse(entry) for entry in data]


def add_user(
    user: UserCreateRequest,
    client: Union[Client, None] = None,
) -> Union[UserResponse, None]:
    """
    Add a user to the database.

    Output:
        Inserted user data as a UserResponse, or None if insert failed.
    """
    if client is None:
        client = get_client()

    data = {
        User_Col_Name.username.value: user.username,
        User_Col_Name.fname.value: user.fname,
        User_Col_Name.lname.value: user.lname,
        User_Col_Name.email.value: user.email,
        User_Col_Name.phone.value: user.phone_num,
        User_Col_Name.passhash.value: user.password,
    }

    response = client.table(USER_TABLE_NAME).insert(data).execute()
    rows = response.data

    if not rows:
        return None

    return create_UserResponse(rows[first])


def remove_user(
    userid: int,
    client: Union[Client, None] = None,
) -> bool:
    """
    Remove a user from the database if they exist.
    Also sets chores assigned to or requested by the user to null.

    Output:
        Returns True if user was removed, False if user did not exist.
    """
    if client is None:
        client = get_client()

    user_in_table = (
        client
        .table(USER_TABLE_NAME)
        .select("*")
        .eq(User_Col_Name.userid.value, userid)
        .maybe_single()
        .execute()
    )

    if not user_in_table.data:
        return False

    client.table("chores").update(
        {"assigned_user": None}
    ).eq("assigned_user", userid).execute()

    client.table("chores").update(
        {"request_user": None}
    ).eq("request_user", userid).execute()

    client.table(USER_TABLE_NAME).delete().eq(
        User_Col_Name.userid.value, userid
    ).execute()

    return True


def is_username_available(
    username: str,
    client: Union[Client, None] = None,
) -> bool:
    """
    Check if a username is available for registration.

    Output:
        True if the username is not taken, False otherwise.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(USER_TABLE_NAME)
        .select("*")
        .eq(User_Col_Name.username.value, username)
        .execute()
    )

    return not response.data


def is_email_available(
    email: str,
    client: Union[Client, None] = None,
) -> bool:
    """
    Check if an email is available for registration.

    Output:
        True if the email is not taken, False otherwise.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(USER_TABLE_NAME)
        .select("*")
        .eq(User_Col_Name.email.value, email)
        .execute()
    )

    return not response.data


def is_phone_num_available(
    phone_num: int,
    client: Union[Client, None] = None,
) -> bool:
    """
    Check if a phone number is available for registration.

    Output:
        True if the phone number is not taken, False otherwise.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(USER_TABLE_NAME)
        .select("*")
        .eq(User_Col_Name.phone.value, phone_num)
        .execute()
    )

    return not response.data

def get_requester(choreid: int, client: Union[Client, None] = None) -> Union[UserResponse, None]:
    """
    Get a requester given a choreid.

    Output:
        A UserResponse matching the requester, or None if chore does not exist.
    """

    if client is None:
        client = get_client()

    response = (client
                .table(CHORE_TABLE_NAME)
                .select(Chore_Col_Name.requester.value)
                .eq(Chore_Col_Name.choreid.value, choreid)
                .execute()
    )

    data = response.data
    if not data:
        return None
    
    requester_id = data[first][Chore_Col_Name.requester.value]
    
    return get_user(userid=requester_id, client=client)
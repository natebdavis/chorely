from collections.abc import Iterable
from typing import Optional
import os
from dotenv import load_dotenv
import pathlib
from supabase import Client, create_client
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.chore import Chore, Notification, Chore_Col_Name, Status
from app.user import User, User_Col_Name
from app.utils import CreateFromDict, load_env_variables, verify_password, TokenData


"""
Module for managing Database operations.
Contributers: Gilligan Berlinski, Nathaniel Davis, Edmund Krajewski
"""

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_client() -> Client:
    """Creates a client to connect with the Supabase Database.
    Raises:
        ValueError: if required environment variables are missing.
        Exception: if client creation fails.
    """

    env = load_env_variables()
    supabase_url = env["SUPABASE_URL"]
    service_key = env["SERVICE_KEY"]

    if supabase_url is None:
        raise ValueError("SUPABASE_URL not found in .env")
    if service_key is None:
        raise ValueError("SERVICE_KEY not found in .env")

    client = create_client(supabase_url, service_key)
    return client

def _get_data_type_list_from_response(data: Optional[Iterable[dict]], 
                                 data_type: CreateFromDict) -> Optional[Iterable[CreateFromDict]]:
    """Helper Function used to create a list of Data Objects given a response from a query.
    Input: `data` an iterable of dictionaries that hold the data of each data object.
            `data_type` the class type that is being represented in the list of dictionaries."""

    data_type_list = []
    if data:
        for entry in data:
            data_type_inst = data_type.from_dict(entry)
            data_type_list.append(data_type_inst)
        return data_type_list
    else:
        return None
    
def _select_all_where_equals_query(table_name: str, col_name: str, value, 
                                   client: Optional[Client] = None) -> Optional [list[dict]]:
    """Helper Function used to select all data from a tables where one column equals the value given."""
    
    if client is None:   
        client = get_client()

    response = client.table(table_name).select("*").eq(col_name, value).execute()

    return response.data

def get_user_by_username(username: str, client: Optional[Client] = None) -> Optional[User]:
    """Get a single `user` given a username.
    Output: A `User` Object created using the first entry matching the username"""

    first = 0
    user_data = _select_all_where_equals_query("users", User_Col_Name.username.value, username, client)
    if user_data[first]:
        return User.from_dict(user_data[first])
    else:
        return None
    
def authenticate_user(username: str, password: str, client: Optional[Client] = None) -> Optional[User]:
    """Authenticate a user given a username and password.
    Output: A `User` Object if the username and password match, `False` otherwise."""
    user = get_user_by_username(username, client)
    if not user:
        return False
    if not verify_password(password, user.passhash):
        return False
    return user

def get_current_user(client: Client = Depends(get_client), token: str = Depends(oauth2_scheme)):
    """Get the current user given a JWT token.
    Output: A `User` Object if the token is valid, raises an HTTPException otherwise."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    env = load_env_variables()
    secret_key = env["SECRET_KEY"]
    algorithm = env["ALGORITHM"]

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        TokenData(username=username)
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(username=username, client=client)
    if user is None:
        raise credentials_exception
    return user

def get_user(userid: int, client: Optional[Client] = None) -> Optional[User]:
    """Get a single `user` given a userid.
    Output: A `User` Object created using the first entry matching the userid"""

    first = 0
    user_data = _select_all_where_equals_query("users", User_Col_Name.userid.value, userid, client)
    if user_data[first]:
        return User.from_dict(user_data[first])
    else:
        return None

def get_users(householdid: int, client: Optional[Client] = None) -> Optional[Iterable[User]]:
    """Get collection of all `users` in household.
    Input: `client` is the connection object used to interact with the database, if none is given
    one is attempted to be created.
    Output: A iterable of `users` that are in the specified household."""
    
    # Fetch all data from the 'users' table
    data = _select_all_where_equals_query("users", User_Col_Name.householdid.value, householdid, client)

    # The data is in response.data
    return _get_data_type_list_from_response(data, User)

def get_chores(householdid: int, client: Optional[Client] = None, 
               users: Optional[Iterable[User]] = None) -> Optional[Iterable[Chore]]:
    """Get collection of all `chores` in household.
    Input: `client` is the connection object used to interact with the database, if none is given
    one is attempted to be created.
    Output: A iterable of `chores` that are in the specified household."""

    # Fetch all data from the 'chores' table
    data = _select_all_where_equals_query("chores", Chore_Col_Name.householdid.value, householdid, client)

    if not users:
        users = get_users(householdid, client)

    for entry in data:

        userid_requester = entry[Chore_Col_Name.requester.value]
        requester = None
        for user in users:
            if user.userid == userid_requester:
                requester = user
                break
        # Check database for user if not in users list
        if not requester:
            userid_requester = entry[Chore_Col_Name.requester.value]
            requester = get_user(userid_requester, client)

        entry[Chore_Col_Name.requester.value] = requester
        

        # Assign User Object if assignee userid has a value
        if entry[Chore_Col_Name.assignee.value]:

            userid_assignee = entry[Chore_Col_Name.assignee.value]
            assignee = None
            for user in users:
                if user.userid == userid_assignee:
                    assignee = user
                    break
            # Check database for user if not in users list
            if not assignee:
                userid_assignee = entry[Chore_Col_Name.assignee.value]
                assignee = get_user(userid_assignee, client)

            entry[Chore_Col_Name.assignee.value] = assignee

    # The data is in data
    return _get_data_type_list_from_response(data, Chore)

def add_user(household: int, user: User, client: Optional[Client] = None):
    """Add user to database"""

    if client is None:
        client = get_client()

    data = {
        User_Col_Name.householdid.value: household,
        User_Col_Name.username.value: user.username,
        User_Col_Name.fname.value: user.fname,
        User_Col_Name.lname.value: user.lname
    }

    response = client.table("users").insert(data).execute()

    return response.data

def remove_user(user: User, client: Optional[Client] = None) -> bool:

    """Removes user from database if user exists. Also removes all notifications associated with the user and sets
    all chores assigned to or requested by the user to null. 
    Output: Returns True if user was removed, False if user did not exist in database."""

    if client is None:
        client = get_client()

    user_in_table = client.table("users").select("*").eq(User_Col_Name.userid.value, user.userid).maybe_single().execute()

    if not user_in_table.data:
        return False
    
    client.table("notifications").delete().eq("userid", user.userid).execute()
    client.table("chores").update({Chore_Col_Name.assignee.value: None}).eq(Chore_Col_Name.assignee.value, user.userid).execute()
    client.table("chores").update({Chore_Col_Name.requester.value: None}).eq(Chore_Col_Name.requester.value, user.userid).execute()
    client.table("users").delete().eq(User_Col_Name.userid.value, user.userid).execute()

    return True

def add_chore(household: int, chore: Chore, client: Optional[Client] = None):
    """
    Add chore to database.

    Inputs:
        household: Household ID the chore belongs to.
        chore: Chore object to insert.
        client: Optional Supabase client.

    Output:
        Inserted row data returned from Supabase.
    """
    if client is None:
        client = get_client()

    data = {
        Chore_Col_Name.householdid.value: household,
        Chore_Col_Name.cname.value: chore.name,
        Chore_Col_Name.description.value: chore.description,
        Chore_Col_Name.request_date.value: chore.request_date.isoformat(),
        Chore_Col_Name.due_date.value: chore.due_date.isoformat(),
        Chore_Col_Name.requester.value: chore.requester.userid,
        Chore_Col_Name.assignee.value: chore.assignee.userid if chore.assignee else None,
        Chore_Col_Name.status.value: chore.status.name,
    }

    response = client.table("chores").insert(data).execute()
    return response.data


def remove_chore(household: int, choreid: int, client: Optional[Client] = None):
    """
    Remove chore from database.

    Inputs:
        household: Household ID the chore belongs to.
        choreid: ID of the chore to delete.
        client: Optional Supabase client.

    Output:
        Deleted row data returned from Supabase.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table("chores")
        .delete()
        .eq(Chore_Col_Name.householdid.value, household)
        .eq(Chore_Col_Name.choreid.value, choreid)
        .execute()
    )

    return response.data

def update_chore(
    household: int,
    choreid: int,
    status: Optional[str] = None,
    assignee_id: Optional[int] = None,
    client: Optional[Client] = None
):
    """
    Update chore data in database.

    Inputs:
        household: Household ID the chore belongs to.
        choreid: Unique identifier of the chore.
        status: Optional new status of the chore.
        assignee_id: Optional new assignee user ID. Use None to unassign.
        client: Optional Supabase client.

    Output:
        Updated row data returned from Supabase.
    """
    if client is None:
        client = get_client()

    data = {}

    if status is not None:
        data[Chore_Col_Name.status.value] = status

    data[Chore_Col_Name.assignee.value] = assignee_id

    response = (
        client
        .table("chores")
        .update(data)
        .eq(Chore_Col_Name.householdid.value, household)
        .eq(Chore_Col_Name.choreid.value, choreid)
        .execute()
    )

    return response.data

def get_all_requested_chores(userid: int, client: Optional[Client] = None) -> Optional[Iterable[Chore]]:
    """Given a userid, return all chores that are requested by the user.
    Output: A iterable of `chores` that are requested by the user."""
    if client is None:
        client = get_client()

    response = (
        client
        .table("chores")
        .select("*")
        .eq(Chore_Col_Name.requester.value, userid)
        .execute()
    )

    return [Chore.from_dict(chore_data) for chore_data in response.data] if response.data else None

def get_all_in_progress_assigned_chores(userid: int, client: Optional[Client] = None) -> Optional[Iterable[Chore]]:
    """Given a userid, return all chores that are assigned to the user and that are in progress.
    Output: A iterable of `chores` that are assigned to the user and in progress."""

    if client is None:
        client = get_client()

    response = (
        client
        .table("chores")
        .select("*")
        .eq(Chore_Col_Name.assignee.value, userid)
        .eq(Chore_Col_Name.status.value, Status.IN_PROGRESS.name)
        .execute()
    )

    return [Chore.from_dict(chore_data) for chore_data in response.data] if response.data else None

def get_all_completed_chores(userid: int, client: Optional[Client] = None) -> Optional[Iterable[Chore]]:
    """Given a userid, return all chores that are assigned to the user and that are completed.
    Output: A iterable of `chores` that are assigned to the user and completed."""

    if client is None:
        client = get_client()

    response = (
        client
        .table("chores")
        .select("*")
        .eq(Chore_Col_Name.assignee.value, userid)
        .eq(Chore_Col_Name.status.value, Status.COMPLETE.name)
        .execute()
    )

    return [Chore.from_dict(chore_data) for chore_data in response.data] if response.data else None


def add_notification(household: int, chore: Chore, notification: Notification):
    """add notification to database"""
    pass

def update_notification(household: int, chore: Chore, notification: Notification):
    """remove notification from database"""
    pass

def remove_notification(household: int, chore: Chore, notification: Notification):
    """change notification data in database"""
    pass



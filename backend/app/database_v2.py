from collections.abc import Iterable
from typing import Union
from supabase import Client, create_client
from jose import JWTError, jwt
from fastapi import Depends

from app.chore_v2 import CHORE_TABLE_NAME, Chore_Col_Name, ChoreResponse, create_ChoreResponse, ChoreCreateRequest
from app.user_v2 import User_Col_Name, USER_TABLE_NAME, UserResponse, create_UserResponse, search_user, UserCreateRequest, UsersToken
from app.utils import load_env_variables, get_password_hash, oauth2_scheme, credentials_exception, verify_password

"""
Module for managing Database operations.
Contributers: Gilligan Berlinski, Nathaniel Davis, Edmund Krajewski
"""

def get_client() -> Client:
    """
    Creates a client to connect with the Supabase Database.

    Output: 
        A Supabase Client object that can be used to interact with the database.

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

async def get_current_user(client: Client = Depends(get_client), token: str = Depends(oauth2_scheme)) -> UserResponse:
    """Get the current user given a JWT token.

    Output: 
        A `User` Object if the token is valid, raises an HTTPException otherwise.
    Raises:
        HTTPException(401) if the token is invalid or if the user does not exist.
    """
    env = load_env_variables()
    secret_key = env["SECRET_KEY"]
    algorithm = env["ALGORITHM"]

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username=username, client=client)
    if user is None:
        raise credentials_exception
    return user

def authenticate_user(username: str, password: str, client: Union[Client, None] = None) -> Union[UserResponse, False]:
    """
    Authenticate a user given a username and password.

    Output: 
        A `User` Object if the username and password match, `False` otherwise.
    """
    user = get_user(username=username, client=client)
    if not user:
        return False
    if not verify_password(password, user.passhash.strip()):
        return False
    return user

def is_username_available(username: str, client: Union[Client, None] = None) -> bool:
    """
    Check if a username is available for registration.

    Output: 
        `True` if the username is not taken, `False` otherwise."""
    if client is None:
        client = get_client()

    response = client.table(USER_TABLE_NAME).select("*").eq(User_Col_Name.username.value, username).execute()
    return not response

def is_email_available(email: str, client: Union[Client, None] = None) -> bool:
    """
    Check if an email is available for registration.

    Output: 
        `True` if the email is not taken, `False` otherwise."""
    if client is None:
        client = get_client()

    response = client.table(USER_TABLE_NAME).select("*").eq(User_Col_Name.email.value, email).execute()
    return not response

def is_phone_num_available(phone_num: int, client: Union[Client, None] = None) -> bool:
    """
    Check if a phone number is available for registration.

    Output: 
        `True` if the phone number is not taken, `False` otherwise."""
    if client is None:
        client = get_client()

    response = client.table(USER_TABLE_NAME).select("*").eq(User_Col_Name.phone.value, phone_num).execute()
    return not response

def get_user(userid: Union[int, None] = None, username: Union[str, None] = None,
              client: Union[Client] = None) -> Union[UserResponse, None]:
    """
    Get a single `user` given a userid or username.

    Output: 
        A `User` Object created using the first entry matching the userid

    Raises:
        Value Error if neither a userid or username have been provided.
    """

    if client is None:
        client = get_client()

    col_name = None
    val = None

    if userid:
        col_name = User_Col_Name.userid.value
        val = userid
    elif username:
        col_name = User_Col_Name.username.value
        val = username
    else:
        raise ValueError("Must provide either a username or userid to search for user.")

    first = 0
    user_data = client.table(USER_TABLE_NAME).select("*").eq(col_name, val).execute()
    if user_data and user_data[first]:
        return create_UserResponse(data=user_data)
    else:
        return None
    
def get_users(householdid: int, client: Union[Client, None] = None) -> Union[Iterable[UserResponse], None]:
    """
    Get collection of all `users` in household.
    
    Output: 
        A iterable of `users` that are in the specified household."""
    
    if client is None:
        client = get_client()
    
    # Fetch all data from the 'users' table
    data = client.table(USER_TABLE_NAME).select("*").eq(User_Col_Name.householdid.value, householdid).execute()

    if data:
        return [create_UserResponse(entry) for entry in data]
    else:
       return None

def get_chore(choreid: int, client: Union[Client, None] = None) -> Union[ChoreResponse, None]:
    """
        Get a single `chore` given a choreid.

    Output: 
        A `Chore` Object created using the first entry matching the choreid"""
    
    if client is None:
        client = get_client()

    first = 0
    chore_data = client.table(CHORE_TABLE_NAME).select("*").eq(Chore_Col_Name.choreid.value, choreid).execute()

    if chore_data and chore_data[first]:
        userid_assignee = chore_data[first][Chore_Col_Name.assignee.value]
        assignee = get_user(userid=userid_assignee, client=client) if userid_assignee else None
        return create_ChoreResponse(data=chore_data, assignee=assignee)
    else:
        return None
    
def get_chores(householdid: int, client: Union[Client, None] = None) -> Union[Iterable[ChoreResponse], None]:
    """
    Get collection of all `chores` in household.
    
    Output: 
    A iterable of `chores` that are in the specified household.

    Raises:
    Value Error if chore is assigned to a user that is not in the chore's household
    """

    if client is None:
        client = get_client()

    
    chore_data = client.table(CHORE_TABLE_NAME).select("*").eq(Chore_Col_Name.householdid.value, householdid).execute()
    user_data = get_users(householdid=householdid, client=client)

    if not chore_data or not user_data:
        return None
    
    chores = []

    for chore in chore_data:
        userid_assignee = chore[Chore_Col_Name.assignee.value]
        user = search_user(userid_assignee)

        if not user:
            error_choreid = chore[Chore_Col_Name.choreid.value]
            raise ValueError(f"Chore id: {error_choreid} has an assignee not apart of the household.")
        
        chores.append(create_ChoreResponse(data=chore, assignee=user))
        
    return chores

def add_user(user: UserCreateRequest, client: Union[Client, None] = None):
    """
    Add user to database

    Output: 
        Inserted row data returned from Supabase.
    """

    if client is None:
        client = get_client()

    passhash = get_password_hash(user.password)

    data = {
        User_Col_Name.username.value: user.username,
        User_Col_Name.fname.value: user.fname,
        User_Col_Name.lname.value: user.lname, 
        User_Col_Name.email.value: user.email,
        User_Col_Name.phone.value: user.phone_num,
        User_Col_Name.passhash.value: passhash
    }

    response = client.table(USER_TABLE_NAME).insert(data).execute()

    if response.data:
        return create_UserResponse(response.data)
    else:
        return None
    
def remove_user(userid: int, client: Union[Client, None] = None) -> bool:

    """
    Removes user from database if user exists. Also removes all notifications associated with the user and sets
    all chores assigned to or requested by the user to null. 
    
    Output: 
        Returns True if user was removed, False if user did not exist in database.
    """

    if client is None:
        client = get_client()

    user_in_table = client.table(CHORE_TABLE_NAME).select("*").eq(User_Col_Name.userid.value, userid).maybe_single().execute()

    if not user_in_table.data:
        return False
    
    client.table(CHORE_TABLE_NAME).update({Chore_Col_Name.assignee.value: None}).eq(Chore_Col_Name.assignee.value, userid).execute()
    client.table(CHORE_TABLE_NAME).update({Chore_Col_Name.requester.value: None}).eq(Chore_Col_Name.requester.value, userid).execute()
    client.table(USER_TABLE_NAME).delete().eq(User_Col_Name.userid.value, userid).execute()

    return True

def add_chore(chore: ChoreCreateRequest, client: Union[Client, None] = None):
    """
    Add chore to database.

    Inputs:
        chore: Chore Create Request to insert.
        client: Optional Supabase client.

    Output:
        Inserted row data returned from Supabase.
    """
    if client is None:
        client = get_client()

    response = client.table(CHORE_TABLE_NAME).insert(chore).execute()

    if response.data:
        return create_ChoreResponse(response.data)
    else:
        return None
    

def remove_chore(householdid: int, choreid: int, client: Union[Client, None] = None) -> bool:
    """
    Remove chore from database.

    Inputs:
        household: Household ID the chore belongs to.
        choreid: ID of the chore to delete.
        client: Optional Supabase client.

    Output:
        `True` if chore was able to be deleted `False` if otherwise.
    """
    if client is None:
        client = get_client()

    response = (client.table(CHORE_TABLE_NAME).delete()
        .eq(Chore_Col_Name.householdid.value, householdid)
        .eq(Chore_Col_Name.choreid.value, choreid)
        .execute()
    )

    return False if not response.data else True

def update_chore(householdid: int, choreid: int, status: Union[str, None] = None, 
                 assignee_id: Union[int, None] = None, client: Union[Client, None] = None) -> Union[ChoreResponse, None]:
    """
    Update chore data in database.

    Inputs:
        householdid: Household ID the chore belongs to.
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
        .table(CHORE_TABLE_NAME)
        .update(data)
        .eq(Chore_Col_Name.householdid.value, householdid)
        .eq(Chore_Col_Name.choreid.value, choreid)
        .execute()
    )

    return None if not response.data else create_ChoreResponse(response.data)

def get_all_requested_chores(userid: int, client: Union[Client, None] = None) -> Union[Iterable[ChoreResponse], None]:
    pass

def get_all_in_progress_assigned_chores(userid: int, client: Union[Client, None] = None) -> Union[Iterable[ChoreResponse], None]:
    pass

def get_all_completed_chores(userid: int, client: Union[Client, None] = None) -> Union[Iterable[ChoreResponse], None]:
    pass

def get_householdid(userid: int, client: Union[Client, None] = None) -> Union[int, None]:
    pass

def household_exists(householdid: int, client: Union[Client, None] = None) -> bool:
    pass

def join_household(userid: int, householdid: int, client: Union[Client, None] = None):
    pass

def leave_household(userid: int, client: Union[Client, None] = None):
    pass

def delete_household_if_empty(householdid: int, client: Union[Client, None] = None) -> bool:
    pass

def get_household_member_count(householdid: int, client: Union[Client, None] = None) -> int:
    pass

def create_household_db(client: Union[Client, None] = None):
    pass


class Notification:
    pass

def add_notification(household: int, choreid: int, notification: Notification):
    """add notification to database"""
    pass

def update_notification(household: int, choreid: int, notification: Notification):
    """remove notification from database"""
    pass

def remove_notification(household: int, choreid: int, notification: Notification):
    """change notification data in database"""
    pass


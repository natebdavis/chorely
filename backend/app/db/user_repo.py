"""
Module for user-related database operations.

Contributors: Edmund Krajewski, Gilligan Berlinski, Nathaniel Davis
"""
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
    UserPasswordUpdateRequest,
    UserProfilePicResponse,
)
from app.chore import CHORE_TABLE_NAME, Chore_Col_Name
from app.utils import verify_password, get_password_hash, BUCKET

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

def get_all_users():
    response = get_client().table("users").select("*").execute()

    if not response.data:
        return []

    return [create_UserResponse(user) for user in response.data]


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
        User_Col_Name.chore_reminder_hours_before_due.value: user.chore_reminder_hours_before_due,
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

def get_profile_pic_url(userid: int, client: Union[Client, None] = None) -> Union[UserProfilePicResponse, None]:
    """
    Get a user's profile picture signed URL (private bucket safe).
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(USER_TABLE_NAME)
        .select(User_Col_Name.profile_url.value)
        .eq(User_Col_Name.userid.value, userid)
        .maybe_single()
        .execute()
    )

    data = response.data
    if not data or not data.get(User_Col_Name.profile_url.value):
        return None

    file_path = data.get(User_Col_Name.profile_url.value)

    if not file_path:
        return None

    file_path = file_path.strip()

    # 🔐 Generate signed URL for private bucket
    signed = client.storage.from_(BUCKET).create_signed_url(
        file_path,
        60 * 60  # 1 hour expiry
    )

    return UserProfilePicResponse(url=signed["signedURL"])

def delete_profile_pic(userid: int, client: Union[Client, None] = None) -> bool:
    """
    Delete a user's profile picture from Supabase storage and update the user's profile URL in the database to null.
    """

    if client is None:
        client = get_client()

    response = (
        client
        .table(USER_TABLE_NAME)
        .select(User_Col_Name.profile_url.value)
        .eq(User_Col_Name.userid.value, userid)
        .single()
        .execute()
    )

    if not response.data:
        return False

    file_path = response.data.get(User_Col_Name.profile_url.value)

    if not file_path:
        return False

    try:
        delete_response = client.storage.from_(BUCKET).remove([file_path])

        if hasattr(delete_response, "error") and delete_response.error:
            raise Exception(delete_response.error)

    except Exception as e:
        raise Exception(f"Failed to delete profile picture: {str(e)}")

    db_response = (
        client
        .table(USER_TABLE_NAME)
        .update({User_Col_Name.profile_url.value: None})
        .eq(User_Col_Name.userid.value, userid)
        .execute()
    )

    if not db_response.data:
        raise Exception("Failed to update user's profile URL in database.")

    return True

def upload_profile_pic(userid: int, profile_path: str, profile_data, profile_file_options: Union[dict, None] = None, client: Union[Client, None] = None) -> dict:
    """
    Upload a user's profile picture to Supabase storage and update the user's profile URL in the database.
    
    Output:
    A dictionary containing the file name and public URL of the uploaded profile picture.
    
    Raises:
    Exception if the upload fails or if updating the user's profile URL in the database fails.
    """

    if client is None:
        client = get_client()

    try:
        response = client.storage.from_(BUCKET).upload(
            path=profile_path,
            file=profile_data,
            file_options=profile_file_options
        )
    except Exception as e:
        raise Exception(f"Failed to upload profile picture: {str(e)}")

    public_url = client.storage.from_(BUCKET).get_public_url(profile_path)

    response = (
        client
        .table(USER_TABLE_NAME)
        .update({User_Col_Name.profile_url.value: profile_path})
        .eq(User_Col_Name.userid.value, userid)
        .execute()
    )

    if not response.data:
        raise Exception("Failed to update user's profile URL in database.")
    
    return {
        "file_name": profile_path,
        "url": public_url
    }

def _get_user_passhash(userid: int, client: Union[Client, None] = None) -> Union[str, None]:
    """
    Get a user's password hash from the database.

    Output:
        The user's password hash as a string, or None if user not found.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(USER_TABLE_NAME)
        .select(User_Col_Name.passhash.value)
        .eq(User_Col_Name.userid.value, userid)
        .maybe_single()
        .execute()
    )

    data = response.data
    if not data:
        return None

    return data[User_Col_Name.passhash.value].strip()

def update_user_password(
    password_update_request: UserPasswordUpdateRequest,
    userid: int,
    client: Union[Client, None] = None,
) -> bool:
    """
    Update a user's password if the old password is correct.

    Output:
        True if the password was updated successfully, False otherwise.

    Raises:
        TypeError if the user is not found.
        ValueError if the old password is incorrect.
    """
    if client is None:
        client = get_client()

    user_response = get_user(userid=userid, client=client)
    if not user_response:
        raise TypeError("User not found.")


    # Verify old password
    if not verify_password(plain_password=password_update_request.old_password, hashed_password=_get_user_passhash(userid=userid, client=client)):
        raise ValueError("Old password is incorrect.")
    
    if password_update_request.old_password == password_update_request.new_password:
        raise ValueError("New password cannot be the same as the old password.")

    hashed_new_password = get_password_hash(password_update_request.new_password)

    # Update to new password
    response = (
        client
        .table(USER_TABLE_NAME)
        .update({User_Col_Name.passhash.value: hashed_new_password})
        .eq(User_Col_Name.userid.value, userid)
        .execute()
    )

    if response.data:
        return True
    else:
        return False
    
def update_chore_reminder_hours_before_due(
    userid: int,
    chore_reminder_hours_before_due: int,
    client: Union[Client, None] = None,
) -> Union[UserResponse, None]:
    """
    Update a user's chore reminder hours before due.
    
    Output:
        The updated user response, or None if the update fails.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(USER_TABLE_NAME)
        .update({
            User_Col_Name.chore_reminder_hours_before_due.value: chore_reminder_hours_before_due
        })
        .eq(User_Col_Name.userid.value, userid)
        .execute()
    )

    rows = response.data
    if not rows:
        return None

    return create_UserResponse(rows[first])



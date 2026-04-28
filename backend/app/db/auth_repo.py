"""
Module for authentication-related database helpers.

Contributors: Edmund Krajewski, Gilligan Berlinski
"""

from typing import Union

from fastapi import Depends
from jose import JWTError, jwt
from supabase import Client

from app.db.client import get_client
from app.user import UserResponse, User_Col_Name, USER_TABLE_NAME, create_UserResponse
from app.utils import (
    load_env_variables,
    oauth2_scheme,
    credentials_exception,
    verify_password,
)

async def get_current_user(
    client: Client = Depends(get_client),
    token: str = Depends(oauth2_scheme),
) -> UserResponse:
    """
    Get the current user from a JWT token.

    Output:
        A UserResponse if the token is valid.

    Raises:
        HTTPException(401) if the token is invalid or the user does not exist.
    """
    env = load_env_variables()
    secret_key = env["SECRET_KEY"]
    algorithm = env["ALGORITHM"]

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(username=username, client=client)
    if user is None:
        raise credentials_exception

    return user


def authenticate_user(
    username: str,
    password: str,
    client: Union[Client, None] = None,
) -> Union[UserResponse, bool]:
    """
    Authenticate a user given a username and password.

    Output:
        A UserResponse if the username and password match, False otherwise.
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

    data = response.data
    if not data:
        return False

    first = 0
    user_row = data[first]

    if not verify_password(password, user_row[User_Col_Name.passhash.value].strip()):
        return False

    return create_UserResponse(user_row)


def get_user_by_username(
    username: str,
    client: Union[Client, None] = None,
) -> Union[UserResponse, None]:
    """
    Get a single user by username.

    Output:
        A UserResponse matching the username, or None if not found.
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

    data = response.data
    if not data:
        return None

    first = 0
    return create_UserResponse(data[first])
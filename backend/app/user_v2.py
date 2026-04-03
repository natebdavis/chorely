from enum import Enum
from pydantic import BaseModel, EmailStr
from typing import Union
from collections.abc import Iterable


"""
Module for managing User operations.
Contributers: Gilligan Berlinski, Nathaniel Davis, Edmund Krajewski
"""

class UserCreateRequest(BaseModel):
    """
    Request body schema for creating a new User.

    Inputs:
        username: Username of the User.
        fname: First name of the User.
        lname: Last name of the User.
        email: Email address of the User.
        phone_num: Phone number of the User.
        password: Password hash for the User.

    Output:
        JSON body representing a User creation request.
    """

    username: str
    fname: str
    lname: str
    email: EmailStr
    phone_num: Union[int, None] = None
    password: str


class UserResponse(BaseModel):
    userid: int
    username: str
    fname: str
    lname: str
    email: Union[EmailStr, None] = None
    phone_num: Union[int, None] = None
    householdid: Union[int, None] = None

class UserInUpdate(BaseModel):
    """
    Request body schema for updating an existing User.

    Inputs:
        userid: Unique identifier for the User to be updated.
        username: Updated username of the User.
        password: Updated password for User. (Password will be hashed before storage)
        fname: Updated first name of the User.
        lname: Updated last name of the User.
        email: Updated email address of the User.
        phone_num: Updated optional phone number.
        householdid: Updated householdid
    """

    userid: int
    username: Union[str, None] = None
    password: Union[str, None] = None
    fname: Union[str, None] = None
    lname: Union[str, None] = None
    email: Union[EmailStr, None] = None
    phone_num: Union[int, None] = None
    householdid: Union[int, None] = None

class UsersToken(BaseModel):
    """
    Response schema for User-related API requests that include an authentication token.
    
    Outputs:
        Token representing the current session of the user.
        Type of the token (e.g., "bearer").
    """
    access_token: str
    token_type: str

USER_TABLE_NAME = "users"

class User_Col_Name(Enum):
    userid = "userid"
    passhash = "passhash"
    username = "username"
    fname = "fname"
    lname = "lname"
    email = "email"
    phone = "phone"
    householdid = "householdid"

def create_UserCreateRequest(data: dict) -> UserCreateRequest:
    return UserCreateRequest(
        username=data[User_Col_Name.username],
        password=data[User_Col_Name.passhash],
        fname=data[User_Col_Name.fname],
        lname=data[User_Col_Name.lname],
        email=data[User_Col_Name.email],
        phone_num=data[User_Col_Name.phone]
    )

def create_UserResponse(data: dict) -> UserResponse:
    return UserResponse(
        userid=data[User_Col_Name.userid],
        username=data[User_Col_Name.username],
        fname=data[User_Col_Name.fname],
        lname=data[User_Col_Name.lname],
        email=data[User_Col_Name.email],
        phone_num=data[User_Col_Name.phone],
        householdid=data[User_Col_Name.householdid])

def create_UserInUpdate(data: dict) -> UserInUpdate:
    return UserInUpdate(
        userid=data[User_Col_Name.userid],
        username=data[User_Col_Name.username],
        password=data[User_Col_Name.passhash],
        fname=data[User_Col_Name.fname],
        lname=data[User_Col_Name.lname],
        email=data[User_Col_Name.email],
        phone_num=data[User_Col_Name.phone],
        householdid=data[User_Col_Name.householdid])

def create_UsersToken(data: dict) -> UsersToken:
    return UsersToken(
        access_token=data["access_token"],
        token_type=data["token_type"]
    )

def get_full_name(user: UserResponse) -> str:
    return user.fname + " " + user.lname

def search_user(userid: int, users: Iterable[UserResponse]) -> Union[UserResponse, None]:

    for user in users:
        if UserResponse.userid == userid:
            return user
        
    return None

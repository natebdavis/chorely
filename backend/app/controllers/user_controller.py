from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

"""
Module for managing User Controller operations.
Handles HTTP requests related to Users and exposes API endpoints
for creating and retrieving Users in the system.

Contributors: Edmund Krajewski
"""

router = APIRouter(tags=["users"])


class UserCreateRequest(BaseModel):
    """
    Request body schema for creating a new User.

    Inputs:
        username: Unique username of the User.
        fname: First name of the User.
        lname: Last name of the User.
        email: Email address of the User.
        phone_num: Optional phone number of the User.
        password: Password of the User.

    Output:
        JSON body representing a User creation request.
    """
    username: str
    fname: str
    lname: str
    email: str
    phone_num: Optional[int] = None
    password: str


class UserResponse(BaseModel):
    """
    Response schema returned for User-related API requests.

    Outputs:
        username: Unique username of the User.
        fname: First name of the User.
        lname: Last name of the User.
        email: Email address of the User.
        phone_num: Optional phone number of the User.
    """
    username: str
    fname: str
    lname: str
    email: str
    phone_num: Optional[int] = None


class TempStoredUser(BaseModel):
    """
    Temporary in-memory User schema used for backend testing.

    Inputs:
        username: Unique username of the User.
        fname: First name of the User.
        lname: Last name of the User.
        email: Email address of the User.
        phone_num: Optional phone number of the User.
        password: Password of the User.

    Output:
        Temporary User object for testing storage and retrieval.
    """
    username: str
    fname: str
    lname: str
    email: str
    phone_num: Optional[int] = None
    password: str


"""
Temporary in-memory storage for Users.

This acts as a placeholder until persistent database-backed
User storage is implemented.
"""
fake_users: List[TempStoredUser] = [
    TempStoredUser(
        username="edmund",
        fname="Edmund",
        lname="Krajewski",
        email="edmund@example.com",
        phone_num=None,
        password="password123"
    ),
    TempStoredUser(
        username="nate",
        fname="Nathaniel",
        lname="Davis",
        email="nate@example.com",
        phone_num=None,
        password="password123"
    ),
]


@router.get("/users", response_model=List[UserResponse])
def get_users():
    """
    Retrieve all Users currently stored.

    Inputs:
        None

    Outputs:
        List of all Users currently in the system, excluding passwords.
    """
    return [
        UserResponse(
            username=user.username,
            fname=user.fname,
            lname=user.lname,
            email=user.email,
            phone_num=user.phone_num
        )
        for user in fake_users
    ]


@router.get("/users/{username}", response_model=UserResponse)
def get_user(username: str):
    """
    Retrieve a single User by username.

    Inputs:
        username: Unique username of the User to retrieve.

    Outputs:
        UserResponse for the requested User.

    Raises:
        HTTPException(404) if the User does not exist.
    """
    for user in fake_users:
        if user.username == username:
            return UserResponse(
                username=user.username,
                fname=user.fname,
                lname=user.lname,
                email=user.email,
                phone_num=user.phone_num
            )

    raise HTTPException(status_code=404, detail="User not found")


@router.post("/users", response_model=UserResponse)
def create_user(request: UserCreateRequest):
    """
    Create a new User.

    Inputs:
        request: UserCreateRequest containing the new User's
                 account and profile information.

    Outputs:
        UserResponse representing the newly created User.

    Raises:
        HTTPException(400) if the username is already taken.
    """
    for user in fake_users:
        if user.username == request.username:
            raise HTTPException(status_code=400, detail="Username already exists")

    new_user = TempStoredUser(
        username=request.username,
        fname=request.fname,
        lname=request.lname,
        email=request.email,
        phone_num=request.phone_num,
        password=request.password
    )

    fake_users.append(new_user)

    return UserResponse(
        username=new_user.username,
        fname=new_user.fname,
        lname=new_user.lname,
        email=new_user.email,
        phone_num=new_user.phone_num
    )
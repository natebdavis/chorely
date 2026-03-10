from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from app.database import get_users, get_user, add_user
from app.user import User

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
        username: Username of the User.
        fname: First name of the User.
        lname: Last name of the User.
        email: Email address of the User.
        phone_num: Optional phone number.
        householdid: Household the user belongs to.

    Output:
        JSON body representing a User creation request.
    """

    username: str
    fname: str
    lname: str
    email: str
    phone_num: Optional[int] = None
    householdid: int


class UserResponse(BaseModel):
    """
    Response schema returned for User-related API requests.

    Outputs:
        username: Username of the User.
        fname: First name of the User.
        lname: Last name of the User.
        email: Email address.
        phone_num: Optional phone number.
    """

    username: str
    fname: str
    lname: str
    email: Optional[str]
    phone_num: Optional[int]


@router.get("/users/{householdid}", response_model=List[UserResponse])
def get_household_users(householdid: int):
    """
    Retrieve all Users belonging to a household.

    Inputs:
        householdid: Identifier of the household.

    Outputs:
        List of UserResponse objects.

    Raises:
        HTTPException(404) if no users exist for that household.
    """

    users = get_users(householdid)

    if not users:
        raise HTTPException(status_code=404, detail="No users found")

    return [
        UserResponse(
            username=u.username,
            fname=u.fname,
            lname=u.lname,
            email=u.email,
            phone_num=u.phone_num,
        )
        for u in users
    ]


@router.get("/user/{userid}", response_model=UserResponse)
def get_single_user(userid: int):
    """
    Retrieve a single User by userid.

    Inputs:
        userid: Unique identifier for the user.

    Outputs:
        UserResponse object.

    Raises:
        HTTPException(404) if user is not found.
    """

    user = get_user(userid)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        username=user.username,
        fname=user.fname,
        lname=user.lname,
        email=user.email,
        phone_num=user.phone_num,
    )


@router.post("/users")
def create_user(request: UserCreateRequest):
    """
    Create a new User in the database.

    Inputs:
        request: UserCreateRequest containing account information.

    Outputs:
        Success message if user creation succeeds.
    """

    user = User(
        username=request.username,
        userid=0,  # placeholder until database assigns ID
        fname=request.fname,
        lname=request.lname,
        email=request.email,
        phone_num=request.phone_num,
    )

    add_user(request.householdid, user)

    return {"message": "User created successfully"}
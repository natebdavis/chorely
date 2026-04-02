from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.database import get_users, get_user, add_user, is_username_available, is_email_available, is_phone_num_available, get_current_user, get_householdid
from app.user import User, UserResponse, UserCreateRequest
from app.utils import get_password_hash

"""
Module for managing User Controller operations.
Handles HTTP requests related to Users and exposes API endpoints
for creating and retrieving Users in the system.

Contributors: Edmund Krajewski
"""

router = APIRouter(tags=["users"], prefix="/user")

@router.get("/{userid}", response_model=UserResponse)
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
        userid=user.userid,
        username=user.username,
        fname=user.fname,
        lname=user.lname,
        email=user.email,
        phone_num=user.phone_num,
    )

@router.get("", response_model=UserResponse, summary="Get my profile (protected)")
def read_me(current_user: UserResponse = Depends(get_current_user)):
    userid = current_user["userid"]
    user = get_user(userid)
    return UserResponse(
        userid=user.userid,
        username=user.username,
        fname=user.fname,
        lname=user.lname,
        email=user.email,
        phone_num=user.phone_num,
        householdid=user.householdid
    )

@router.post("/create")
def create_user(request: UserCreateRequest):
    """
    Create a new User in the database.

    Inputs:
        request: UserCreateRequest containing account information.

    Outputs:
        Success message if user creation succeeds.
    """

    if not is_username_available(request.username):
        raise HTTPException(status_code=409, detail="Username not available")

    if not is_email_available(request.email):
        raise HTTPException(status_code=409, detail="Email not available")

    if request.phone_num is not None and not is_phone_num_available(request.phone_num):
        raise HTTPException(status_code=409, detail="Phone number not available")
    
    hashed_password = get_password_hash(request.password)

    user = User(
        username=request.username,
        passhash=hashed_password,
        userid=0,  # placeholder until database assigns ID
        fname=request.fname,
        lname=request.lname,
        email=request.email,
        phone_num=request.phone_num,
    )

    response = add_user(user)

    return {"message": "User created successfully", "userid": response[0]["userid"]}


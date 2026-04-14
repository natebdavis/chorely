from fastapi import APIRouter, Depends, HTTPException

from app.database import (
    get_user,
    add_user,
    is_username_available,
    is_email_available,
    is_phone_num_available,
    get_current_user,
)
from app.user import UserResponse, UserCreateRequest
from app.utils import get_password_hash

"""
Module for managing User Controller operations.
Handles HTTP requests related to Users and exposes API endpoints
for creating and retrieving Users in the system.

Contributors: Edmund Krajewski, Gilligan Berlinski
"""

router = APIRouter(tags=["users"], prefix="/user")


@router.get("/by-username/{username}", response_model=UserResponse)
def get_user_by_username_route(username: str):
    """
    Retrieve a single user by username.
    """
    user = get_user(username=username)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


@router.get("/{userid}", response_model=UserResponse)
def get_single_user(userid: int):
    """
    Retrieve a single user by userid.
    """
    user = get_user(userid=userid)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("", response_model=UserResponse, summary="Get my profile (protected)")
def read_me(current_user: UserResponse = Depends(get_current_user)):
    """
    Retrieve the profile of the currently authenticated user.
    """
    return current_user


@router.post("/create")
def create_user(request: UserCreateRequest):
    """
    Create a new user in the database.
    """
    if not is_username_available(request.username):
        raise HTTPException(status_code=409, detail="Username not available")

    if not is_email_available(request.email):
        raise HTTPException(status_code=409, detail="Email not available")

    if request.phone_num is not None and not is_phone_num_available(request.phone_num):
        raise HTTPException(status_code=409, detail="Phone number not available")

    request.password = get_password_hash(request.password)
    created_user = add_user(request)

    if not created_user:
        raise HTTPException(status_code=500, detail="Failed to create user")

    return {
        "message": "User created successfully",
        "userid": created_user.userid,
    }
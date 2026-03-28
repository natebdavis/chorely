from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
from app.utils import Token, create_access_token
from app.database import get_current_user, authenticate_user
from app.user import UserResponse

"""
Module for managing Authentication Controller operations.
Handles HTTP requests related to user authentication and exposes
API endpoints for logging users into the system.

Contributors: Edmund Krajewski
"""

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    """
    Request body schema for logging a User into the system.

    Inputs:
        username: Username of the User attempting to log in.
        password: Password of the User attempting to log in.

    Output:
        JSON body representing a login request.
    """
    username: str
    password: str


class LoginResponse(BaseModel):
    """
    Response schema returned for login API requests.

    Outputs:
        success: True if login was successful, False otherwise.
        message: Status message describing the login result.
    """
    success: bool
    message: str


class TempUser(BaseModel):
    """
    Temporary User schema used for in-memory authentication testing.

    Inputs:
        username: Username of the test User.
        password: Password of the test User.

    Output:
        Temporary User object for authentication checks.
    """
    username: str
    password: str


"""
Temporary in-memory storage for Users.

This acts as a placeholder until persistent database-backed
authentication is implemented.
"""
fake_users: List[TempUser] = [
    TempUser(username="edmund", password="password123"),
    TempUser(username="nate", password="password123"),
    TempUser(username="gilligan", password="password123"),
]

@router.post("/login", response_model=Token)
def login_for_access_token(request: OAuth2PasswordRequestForm = Depends()):
    """ 
    Attempt to log a User into System and generate a session token if successful

    Inputs:
        request: Standard Login form with username and password

    Outputs:
        Token representing the current session of the user

    Raises:
        HTTPException(401) if the username or password is incorrect.
    """

    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse, summary="Get my profile (protected)")
def read_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user
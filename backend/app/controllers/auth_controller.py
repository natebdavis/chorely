from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

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


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    """
    Attempt to log a User into the system.

    Inputs:
        request: LoginRequest containing the username and password
                 entered by the User.

    Outputs:
        LoginResponse indicating whether authentication succeeded.

    Raises:
        HTTPException(401) if the username or password is incorrect.
    """
    for user in fake_users:
        if user.username == request.username and user.password == request.password:
            return LoginResponse(
                success=True,
                message="Login successful"
            )

    raise HTTPException(status_code=401, detail="Invalid username or password")
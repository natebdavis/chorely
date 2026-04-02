from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.utils import Token, create_access_token
from app.database import authenticate_user, is_username_available, get_current_user
from app.user import UserResponse

"""
Module for managing Authentication Controller operations.
Handles HTTP requests related to user authentication and exposes
API endpoints for logging users into the system.

Contributors: Edmund Krajewski, Gilligan Berlinski
"""

router = APIRouter(tags=["auth"], prefix="/auth")

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

    if is_username_available(request.username):
        raise HTTPException(status_code=401, detail="No user with that username exists.")

    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

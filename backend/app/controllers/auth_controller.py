"""
Module for managing Authentication Controller operations.
Handles HTTP requests related to user authentication and exposes
API endpoints for logging users into the system.

Contributors: Edmund Krajewski, Gilligan Berlinski
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.database import authenticate_user
from app.utils import Token, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
""" API router for authentication-related endpoints. All routes defined in this module"""


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Authenticate a user and return a bearer token.
    """
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})

    return Token(
        access_token=access_token,
        token_type="bearer",
    )
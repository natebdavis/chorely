"""
Module for managing Leaderboard Controller operations.
Handles HTTP requests related to household leaderboards and exposes
API endpoints for retrieving leaderboard statistics for the current user's household.

Contributors: Gilligan Berlinski
"""
from fastapi import APIRouter, HTTPException, status, Depends

from app.leaderboard import Leaderboard_Response
from app.user import UserResponse
from app.database import (
    get_leaderboard as db_get_leaderboard,
    get_current_user,
)

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])
""" API router for leaderboard-related endpoints."""

@router.get("", response_model=list[Leaderboard_Response])
def get_leaderboard(
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Retrieve current user's household leaderboard statistics.
    Statistics include total number of chores each user has completed and the percentage of total household chores they have completed.

    Raises:
    - HTTPException 400: If current user is not part of a household.
    - HTTPException 404: If the leaderboard could not be found for the user's household.
    """
    if current_user.householdid is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not part of a household",
        )

    leaderboard = db_get_leaderboard(current_user.householdid)

    if not leaderboard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leaderboard not found",
        )

    return leaderboard
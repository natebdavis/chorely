"""
Module for leaderboard database operations.

Contributors: Gilligan Berlinski
"""
from supabase import Client
from typing import Union, Iterable

from app.db.client import get_client
from app.leaderboard import Leaderboard_Response, create_leaderboard_response, LEADERBOARD_VIEW, Leaderboard_Col_Name


def get_leaderboard(householdid: int, client: Union[Client, None] = None) -> Iterable[Leaderboard_Response]:
    """
    Get a household's leaderboard statistics given a householdid.
    """

    if client is None:
        client = get_client()

    response = (
        client
        .table(LEADERBOARD_VIEW)
        .select("*")
        .eq(Leaderboard_Col_Name.householdid.value, householdid)
        .execute()
    )

    data = response.data

    if not data:
        return None
    
    return create_leaderboard_response(data)
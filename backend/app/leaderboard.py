from enum import Enum
from typing import Iterable
from pydantic import BaseModel

"""
Module for managing leaderboard operations.

Contributors: Gilligan Berlinski
"""

LEADERBOARD_VIEW = "leaderboard_view"

class Leaderboard_Col_Name(Enum):
    householdid = "householdid"
    username = "username"
    userid = "assigned_user"
    chores_completed = "chores_complete"
    percent_of_chores = "percent_of_household"

class Leaderboard_Response(BaseModel):
    householdid: int
    username: str
    userid: int
    chores_completed: int
    percent_of_chores: int

def create_leaderboard_response(data: dict) -> Iterable[Leaderboard_Response]:
    return list(Leaderboard_Response(
        householdid=entry[Leaderboard_Col_Name.householdid.value],
        username=entry[Leaderboard_Col_Name.username.value],
        userid=entry[Leaderboard_Col_Name.userid.value],
        chores_completed=entry[Leaderboard_Col_Name.chores_completed.value],
        percent_of_chores=entry[Leaderboard_Col_Name.percent_of_chores.value]) for entry in data)
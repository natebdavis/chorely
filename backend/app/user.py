from collections.abc import Iterable
from typing import Set

from backend.app.chore import Chore, Notification


class User:
    """A roommate"""
    username: str
    fname: str
    lname: str
    email: str
    phone: int

    def __init__(self, username: str, fname: str, lname: str, email: str, phone: int):
        """Constructor for User"""
        self.username = username
        self.fname = fname
        self.lname = lname
        self.email = email
        self.phone = phone

def get_chores(user: User, chores: Iterable[Chore]) -> Set[Chore]:
    """Get all chores that a user is assigned to"""
    return {chore for chore in chores if chore.assignee == user}

def get_notifs(user: User, chores: Iterable[Chore]) -> Set[Notification]:
    """Get all notifications for chores that a user is assigned to"""
    notifications: Set[Notification] = set()
    for chore in chores:
        if chore.assignee == user:
            notifications.update(chore.notifications)
    return notifications
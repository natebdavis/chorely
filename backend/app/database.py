from collections.abc import Iterable

from app.chore import Chore, Notification
from app.user import User

"""
Module for managing operations with the local and server database.
Contributers: Nathaniel Davis
"""

def get_users(household: int) -> Iterable[User]:
    """get collection of all users in household"""
    pass

def get_chores(household: int) -> Iterable[Chore]:
    """get collection of all users in household"""
    pass

def check_updates(users: Iterable[User], chores: Iterable[Chore]) -> bool:
    """check if server database is different from user database"""
    pass

def fetch(users: Iterable[User], chores: Iterable[Chore]):
    """get changes from server"""
    pass

def add_user(household: int, user: User):
    """add user to database"""
    pass

def remove_user(household: int, user: User):
    """remove user from database"""
    pass

def add_chore(household: int, chore: Chore):
    """add chore to database"""
    pass

def remove_chore(household: int, chore: Chore):
    """remove chore from database"""
    pass

def update_chore(household: int, chore: Chore):
    """change chore data in database"""
    pass

def add_notification(household: int, chore: Chore, notification: Notification):
    """add notification to database"""
    pass

def update_notification(household: int, chore: Chore, notification: Notification):
    """remove notification from database"""
    pass

def remove_notification(household: int, chore: Chore, notification: Notification):
    """change notification data in database"""
    pass


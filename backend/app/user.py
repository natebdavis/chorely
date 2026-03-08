from typing import Optional
import re
from collections.abc import Iterable
from typing import Set

from backend.app.chore import Chore, Notification


"""
Module for managing User operations.
Contributers: Gilligan Berlinski, Nathaniel Davis
"""
class User:
    """User."""

    username: str
    fname: str
    lname: str
    phone_num: Optional[int]
    """Optional information, user can attach their phone number to their account."""
    _EMAIL_REGULAR_EXPRESSION = "[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}"
    """Regular expression for validating email."""

    def __init__(self, username: str, fname: str, lname: str, email: str, 
                 phone_num: Optional[int] = None):
        """Constructor for User Class.
        Inputs: `email` will be checked if it is a valid email, if not then it is set to null.
        `phone_num` can be null or have a value upon creation of the user object.
        Output: `User` Object
        """
        self.username = username
        self.fname = fname
        self.lname = lname
        self.phone_num = phone_num
        self.email = email if self.__isValidEmail(email) else None

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, email: str) -> bool:
        """Setter for `email` if a valid email is given change the email to the new one, if not keep
        the original email.
        Output: `True` if was able to change email to new value, `False` if otherwise."""
        if self.__isValidEmail(email):
            self._email = email
            return True
        else:
            return False
        
    def __isValidEmail(self, email: str) -> bool:
         """Private Method for checking if email given is in a valid format.
         Output: `True` if email is valid, `False` if otherwise."""
         valid_email = re.match(self._EMAIL_REGULAR_EXPRESSION, email)
         return True if valid_email else False

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
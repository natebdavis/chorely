from typing import Optional
import re
from collections.abc import Iterable
from typing import Set
from enum import Enum, auto
from app.chore import Chore, Notification
from app.misc import CreateFromDict


"""
Module for managing User operations.
Contributers: Gilligan Berlinski, Nathaniel Davis
"""

class User_Col_Name(Enum):
    userid = "userid"
    passhash = "passhash"
    username = "username"
    fname = "fname"
    lname = "lname"
    email = "email"
    phone = "phone"
    householdid = "householdid"

class User(CreateFromDict):
    """User."""

    username: str
    fname: str
    lname: str
    phone_num: Optional[int]
    """Optional information, user can attach their phone number to their account."""
    _EMAIL_REGULAR_EXPRESSION = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}"
    """Regular expression for validating email."""

    def __init__(self, username: str, userid: int, fname: str, lname: str, email: str, 
                 phone_num: Optional[int] = None):
        """Constructor for User Class.
        Inputs: `email` will be checked if it is a valid email, if not then it is set to null.
        `phone_num` can be null or have a value upon creation of the user object.
        Output: `User` Object
        """
        self.username = username
        self.userid = userid
        self.fname = fname
        self.lname = lname
        self.phone_num = phone_num
        self.email = email if self.__isValidEmail(email) else None

    @classmethod
    def from_dict(cls, user_dict: dict):
        """Alternate Constructor for `User`
        Input: Dictionary with all values assoicated with a `User`"""
        username = user_dict[User_Col_Name.username.value]
        userid = user_dict[User_Col_Name.userid.value]
        fname = user_dict[User_Col_Name.fname.value]
        lname = user_dict[User_Col_Name.lname.value]
        email = user_dict[User_Col_Name.email.value]
        phone = user_dict[User_Col_Name.phone.value]

        return cls(username, userid, fname, lname, email = email, phone_num = phone)
<<<<<<< Updated upstream
=======
    
    @property
    def full_name(self) -> str:
        """Return the user's full name."""
        return f"{self.fname} {self.lname}"
>>>>>>> Stashed changes

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, email) -> bool:
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

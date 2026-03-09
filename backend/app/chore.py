from collections.abc import Iterable
import datetime as DT
from typing import Optional
from user import User
from enum import Enum, auto
import pytz

from misc import CreateFromDict

"""
Module for managing Chore operations.
Contributers: Gilligan Berlinski
"""

class Chore_Col_Name(Enum):
    cname = "cname"
    description = "descrip"
    request_date = "request_date"
    due_date = "due_date"
    requester = "request_user"
    assignee = "assigned_user"
    status = "cstatus"
    householdid = "householdid"

class Status(Enum):
    """Status of Chore."""
    UNASSIGNED = auto()
    IN_PROGRESS = auto()
    COMPLETE = auto()
    CANCELLED = auto()

class Notification:
    """Notification for a Chore."""
    time: DT.datetime

    def __init__(self, time: DT.datetime):
        """Constructor for Notification"""
        self.time = time

class Chore(CreateFromDict):
    """Chore."""
    name: str
    description: str
    request_date: DT.datetime
    due_date: DT.datetime
    requester: User
    """User who requested the Chore."""
    notifications: Iterable[Notification]

    def __init__(self, name: str, description: str, request_date: Optional[DT.datetime], 
                 due_date: DT.datetime, requester: User, assignee: Optional[User], 
                 status: Optional[Status]):
        """Constructor for Chore Class.
        Inputs: `Assignee` can be initially null or can be assigned on creation, 
        `request_date` will be auto-generated on creation if not given, `status` will be set to
        UNASSIGNED if `assignee` is null or IN-PROGRESS if a User is assigned to the chore.
        Output: `Chore` Object
        """
        self.name  = name
        self.description = description
        self.request_date = request_date if request_date else DT.datetime.now(pytz.utc)
        self.due_date = due_date
        self.requester = requester
        self._assignee = assignee
        
        if status:
            self._status = status
        else:
            self._status = Status.IN_PROGRESS if self._assignee else Status.UNASSIGNED

        self.notifications = set()

    @classmethod
    def from_dict(cls, chore_dict: dict):
        """Alternate Constructor for `Chore`
        Input: Dictionary with all values assoicated with a `Chore`"""
        name = chore_dict[Chore_Col_Name.cname.value]
        description = chore_dict[Chore_Col_Name.description.value]
        request_date = DT.datetime.fromisoformat(chore_dict[Chore_Col_Name.request_date.value])
        due_date = DT.datetime.fromisoformat(chore_dict[Chore_Col_Name.due_date.value])
        requester = chore_dict[Chore_Col_Name.requester.value]
        assignee = chore_dict[Chore_Col_Name.assignee.value]
        status = Status[chore_dict[Chore_Col_Name.status.value]]

        return cls(name, description, request_date, due_date, requester, assignee, status)

    @property
    def status(self) -> Status:
        return self._status
    
    @status.setter
    def status(self, status: Status):
        self._status = status
    
    @property
    def assignee(self) -> Optional[User]:
        """User that is tasked with completeing the `Chore`."""
        return self._assignee
    
    @assignee.setter
    def assignee(self, assignee: Optional[User]):
        """Setter for `assignee`, if `assignee` was null and given a new `User` also
        change the `Chore`'s `status` to In Progress. If given null as the new `assignee`
        value then change `status` to unassigned."""
        if not self._assignee and assignee:
            self.status = Status.IN_PROGRESS
        elif self._assignee and not assignee:
            self.status = Status.UNASSIGNED
        self._assignee = assignee


'''
Issue with Code can not have two files import each other at same time,
maybe have database.py handle these operations instead.

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
'''

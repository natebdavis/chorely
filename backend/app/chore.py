from collections.abc import Iterable
import datetime as DT
from typing import Optional
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.user import User
from enum import Enum, auto
import pytz

"""
Module for managing Chore operations.
Contributers: Gilligan Berlinski, Nathaniel Davis
"""

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

class Chore:
    """Chore."""
    name: str
    description: str
    request_date: DT.datetime
    due_date: DT.datetime
    requester: "User"
    """User who requested the Chore."""
    notifications: Iterable[Notification]

    ddef __init__(self, name: str, description: str, due_date: DT.datetime, requester: "User",
             assignee: Optional["User"] = None):
        """Constructor for Chore Class.
        Inputs: `Assignee` can be initially null or can be assigned on creation, 
        `request_date` will be auto-generated on creation, `status` will be set to
        UNASSIGNED if `assignee` is null or IN-PROGRESS if a User is assigned to the chore.
        Output: `Chore` Object
        """
        self.name  = name
        self.description = description
        self.request_date = DT.datetime.now(pytz.utc)
        self.due_date = due_date
        self.requester = requester
        self._assignee = assignee
        self.request_date = DT.datetime.now(pytz.utc)
        self._status = Status.IN_PROGRESS if self._assignee else Status.UNASSIGNED
        self.notifications = set()

    @property
    def status(self) -> Status:
        return self._status
    
    @status.setter
    def status(self, status: Status):
        self._status = status
    
    @property
    def assignee(self) -> Optional["User"]:
        """User that is tasked with completeing the `Chore`."""
        return self._assignee
    
    @assignee.setter
    def assignee(self, assignee: Optional["User"]):
        """Setter for `assignee`, if `assignee` was null and given a new `User` also
        change the `Chore`'s `status` to In Progress. If given null as the new `assignee`
        value then change `status` to unassigned."""
        if not self._assignee and assignee:
            self.status = Status.IN_PROGRESS
        elif self._assignee and not assignee:
            self.status = Status.UNASSIGNED
        self._assignee = assignee

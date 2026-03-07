from collections.abc import Iterable
import datetime as DT
from typing import Optional
from user import User
from enum import Enum, auto
import pytz

"""
Module for managing Chore operations.
Contributers: Gilligan Berlinski
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
    requester: User
    """User who requested the Chore."""
    assignee: Optional[User]
    """User tasked with Completing Chore."""
    status: Status
    notifications: Iterable[Notification]

    def __init__(self, name: str, description: str, due_date: DT.datetime, requester: User, 
                 assignee: Optional[User] = None):
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
        self.assignee = assignee
        if (assignee != None):
            self.status = Status.IN_PROGRESS
        else:
            self.status = Status.UNASSIGNED
        self.notifications = set()

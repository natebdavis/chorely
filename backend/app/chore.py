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
    time = DT.datetime

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
    notification: Optional[Iterable[Notification]]

    def __init__(self, name: str, description: str, due_date: DT.datetime, requester: User, 
                 assignee: User = None):
        """Constructor for Chore Class.
        Inputs: `Assignee` can be initially null or can be assigned on creation, 
        `request_date` will be auto-generated on creation, `status` will be set to
        UNASSIGNED if `assignee` is null or IN-PROGRESS if a User is assigned to the chore.
        Output: `Chore` Object
        """
        self = self
        self.name  = name
        self.description = description
        self.due_date = due_date
        self.assignee = assignee
        self.request_date = DT.datetime.now(pytz.utc)

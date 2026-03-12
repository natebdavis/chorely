from collections.abc import Iterable
import datetime as DT
from typing import Optional, TYPE_CHECKING
from enum import Enum, auto
import pytz

from app.misc import CreateFromDict

if TYPE_CHECKING:
    from app.user import User

"""
Module for managing Chore operations.
Contributers: Gilligan Berlinski, Nathaniel Davis, Edmund Krajewski
"""


class Chore_Col_Name(Enum):
    choreid = "choreid"
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
    choreid: Optional[int]
    name: str
    description: str
    request_date: DT.datetime
    due_date: DT.datetime
    requester: "User"
    notifications: Iterable[Notification]

    def __init__(
        self,
        name: str,
        description: str,
        due_date: DT.datetime,
        requester: "User",
        choreid: Optional[int] = None,
        assignee: Optional["User"] = None,
        request_date: Optional[DT.datetime] = None,
        status: Optional[Status] = None
    ):
        """
        Constructor for Chore Class.

        Inputs:
            assignee can be initially null or assigned on creation.
            request_date will be auto-generated on creation if not given.
            status will be set to UNASSIGNED if assignee is null or
            IN_PROGRESS if a User is assigned to the chore unless explicitly given.

        Output:
            Chore object
        """
        self.choreid = choreid
        self.name = name
        self.description = description
        self.request_date = request_date if request_date else DT.datetime.now(pytz.utc)
        self.due_date = due_date
        self.requester = requester
        self._assignee = assignee

        if status is not None:
            self._status = status
        else:
            self._status = Status.IN_PROGRESS if self._assignee else Status.UNASSIGNED

        self.notifications = set()

    @classmethod
    def from_dict(cls, chore_dict: dict):
        """Alternate constructor for Chore from a dictionary."""
        name = chore_dict[Chore_Col_Name.cname.value]
        choreid = chore_dict[Chore_Col_Name.choreid.value]
        description = chore_dict[Chore_Col_Name.description.value]
        request_date = DT.datetime.fromisoformat(
            chore_dict[Chore_Col_Name.request_date.value]
        )
        due_date = DT.datetime.fromisoformat(
            chore_dict[Chore_Col_Name.due_date.value]
        )
        requester = chore_dict[Chore_Col_Name.requester.value]
        assignee = chore_dict[Chore_Col_Name.assignee.value]
        status = Status[chore_dict[Chore_Col_Name.status.value]]

        return cls(
            name=name,
            description=description,
            due_date=due_date,
            requester=requester,
            choreid=choreid,
            assignee=assignee,
            request_date=request_date,
            status=status
        )

    @property
    def status(self) -> Status:
        return self._status

    @status.setter
    def status(self, status: Status):
        self._status = status

    @property
    def assignee(self) -> Optional["User"]:
        """User that is tasked with completing the Chore."""
        return self._assignee

    @assignee.setter
    def assignee(self, assignee: Optional["User"]):
        """
        If assignee was null and gets a user, set status to IN_PROGRESS.
        If assignee becomes null, set status to UNASSIGNED.
        """
        if not self._assignee and assignee:
            self.status = Status.IN_PROGRESS
        elif self._assignee and not assignee:
            self.status = Status.UNASSIGNED
        self._assignee = assignee

    def createBaseModel(self) -> dict:
        """
        Create a dictionary representation of a Chore suitable for API responses.
        """
        assignee = None if not self.assignee else f"{self.assignee.fname} {self.assignee.lname}"

        return {
            "choreid": self.choreid,
            "name": self.name,
            "description": self.description,
            "request_date": int(self.request_date.timestamp()) if self.request_date else None,
            "due_date": int(self.due_date.timestamp()) if self.due_date else None,
            "assignee": assignee,
            "status": self.status.name if self.status else None,
        }
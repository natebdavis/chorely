from collections.abc import Iterable
import datetime as DT
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from app.user import User
from enum import Enum, auto
import pytz

from app.misc import CreateFromDict

"""
Module for managing Chore operations.
Contributers: Gilligan Berlinski, Nathaniel Davis, Edmund Krajewski
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
        self.time = time

<<<<<<< Updated upstream
=======
class ChoreCreateRequest(BaseModel):
    """
    Request body schema for creating a new Chore.

    Inputs:
        name: Name/title of the chore.
        description: Optional detailed description of the chore.
        assigned_to: Optional username of the user assigned to the chore.

    Output:
        JSON body representing the chore creation request.
    """
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1, max_length=3000)
    assigned_to: Optional[str] = None

class ChoreResponse(BaseModel):
    """
    Response schema returned for Chore-related API requests.

    Outputs:
        choreid: Unique identifier of the Chore.
        name: Name of the Chore.
        description: Description of the Chore.
        request_date: Unix timestamp representing when the Chore was requested.
        due_date: Unix timestamp representing when the Chore is due.
        assignee: Full name of the assignee, or null if unassigned.
        status: Current status of the Chore.
    """
    choreid: Optional[int] = None
    name: str
    description: str
    request_date: Optional[int] = None
    due_date: Optional[int] = None
    assignee: Optional[str]
    status: str
>>>>>>> Stashed changes

class Chore(CreateFromDict):
    """Chore."""
    name: str
    description: str
    request_date: DT.datetime
    due_date: DT.datetime
    requester: "User"
    notifications: Iterable[Notification]

<<<<<<< Updated upstream
    def __init__(
        self,
        name: str,
        description: str,
        due_date: DT.datetime,
        requester: "User",
        assignee: Optional["User"] = None,
        request_date: Optional[DT.datetime] = None,
        status: Optional["Status"] = None,
    ):
=======
    # def __init__(self, name: str, choreid: int, description: str, request_date: DT.datetime,
    #               due_date: DT.datetime, requester: "User",
    #          assignee: Optional["User"] = None, status: Optional[Status] = None):

    def __init__(self, name: str, description: str, due_date: DT.datetime, requester: "User", choreid: Optional[int] = None, assignee: Optional["User"] = None,
                 request_date: Optional[DT.datetime] = None, status: Optional[Status] = None):
        """Constructor for Chore Class.
        Inputs: `Assignee` can be initially null or can be assigned on creation, 
        `request_date` will be auto-generated on creation if not given, `status` will be set to
        UNASSIGNED if `assignee` is null or IN-PROGRESS if a User is assigned to the chore.
        Output: `Chore` Object
>>>>>>> Stashed changes
        """
        Constructor for Chore Class.
        assignee can be null or assigned on creation.
        request_date auto-generates if not given.
        status becomes UNASSIGNED if assignee is null, otherwise IN_PROGRESS,
        unless explicitly provided.
        """
        self.name = name
        self.description = description
        self.request_date = request_date if request_date else DT.datetime.now(pytz.utc)
        self.due_date = due_date
        self.requester = requester
        self._assignee = assignee

<<<<<<< Updated upstream
        if status is not None:
=======

        if status:
>>>>>>> Stashed changes
            self._status = status
        else:
            self._status = Status.IN_PROGRESS if self._assignee else Status.UNASSIGNED

        self.notifications = set()

    @classmethod
    def from_dict(cls, chore_dict: dict):
        """Alternate constructor for Chore from a dictionary."""
        name = chore_dict[Chore_Col_Name.cname.value]
        description = chore_dict[Chore_Col_Name.description.value]
        request_date = DT.datetime.fromisoformat(chore_dict[Chore_Col_Name.request_date.value])
        due_date = DT.datetime.fromisoformat(chore_dict[Chore_Col_Name.due_date.value])
        requester = chore_dict[Chore_Col_Name.requester.value]
        assignee = chore_dict[Chore_Col_Name.assignee.value]
        status = Status[chore_dict[Chore_Col_Name.status.value]]

<<<<<<< Updated upstream
        return cls(
            name=name,
            description=description,
            due_date=due_date,
            requester=requester,
            assignee=assignee,
            request_date=request_date,
            status=status,
        )
=======

        # return cls(name, choreid, description, request_date, due_date, requester, assignee, status)
        return cls(name=name, description=description, due_date=due_date, requester=requester, choreid=choreid, assignee=assignee, request_date=request_date, status=status)
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
    def createBaseModel(self) -> dict:
        """
        Create a dictionary representation of a Chore suitable for API responses.
        Output: Dictionary containing frontend-safe chore data.
        """
        return {
=======
    def get_chore_request_model(self) -> ChoreCreateRequest:
        assigned_to = None if not self.assignee else self.assignee.full_name
        return ChoreCreateRequest(name=self.name,
                                  description=self.description,
                                  assigned_to=assigned_to)
    
    # def get_chore_response_model(self) -> ChoreResponse:
    #     """
    #     Create a ChoreResponse object suitable for API responses.
    #     """
    #     assigned_to = None if not self.assignee else f"{self.assignee.fname} {self.assignee.lname}"
    #     return ChoreResponse(
    #         name=self.name,
    #         description=self.description,
    #         assigned_to=assigned_to,
    #         status=self.status.name
    #     )

    def createBaseModel(self) -> dict:
        """
        Create a dictionary representation of a Chore suitable for API responses.
        """
        assignee = None if not self.assignee else f"{self.assignee.fname} {self.assignee.lname}"

        return {
            "choreid": self.choreid,
>>>>>>> Stashed changes
            "name": self.name,
            "description": self.description,
            "request_date": int(self.request_date.timestamp()) if self.request_date else None,
            "due_date": int(self.due_date.timestamp()) if self.due_date else None,
<<<<<<< Updated upstream
            "assignee": f"{self.assignee.fname} {self.assignee.lname}" if self.assignee else None,
            "status": self.status.name if self.status else None,
        }


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
=======
            "assignee": assignee,
            "status": self.status.name if self.status else None,
        }
>>>>>>> Stashed changes

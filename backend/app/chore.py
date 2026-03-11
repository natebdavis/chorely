from collections.abc import Iterable
import datetime as DT
from typing import Optional
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.user import User
from enum import Enum, auto
import pytz
from pydantic import BaseModel, Field

from misc import CreateFromDict

"""
Module for managing Chore operations.
Contributers: Gilligan Berlinski, Nathaniel Davis, Edmund Krajewski
"""

class Chore_Col_Name(Enum):
    cname = "cname"
    choreid = "choreid"
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
    choreid: int
    description: str
    request_date: DT.datetime
    due_date: DT.datetime
    requester: "User"
    """User who requested the Chore."""
    notifications: Iterable[Notification]

    def __init__(self, name: str, choreid: int, description: str, request_date: DT.datetime,
                  due_date: DT.datetime, requester: "User",
             assignee: Optional["User"] = None, status: Optional[Status] = None):
        """Constructor for Chore Class.
        Inputs: `Assignee` can be initially null or can be assigned on creation, 
        `request_date` will be auto-generated on creation if not given, `status` will be set to
        UNASSIGNED if `assignee` is null or IN-PROGRESS if a User is assigned to the chore.
        Output: `Chore` Object
        """
        self.choreid = choreid
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
        choreid = chore_dict[Chore_Col_Name.choreid.value]
        description = chore_dict[Chore_Col_Name.description.value]
        request_date = DT.datetime.fromisoformat(chore_dict[Chore_Col_Name.request_date.value])
        due_date = DT.datetime.fromisoformat(chore_dict[Chore_Col_Name.due_date.value])
        requester = chore_dict[Chore_Col_Name.requester.value]
        assignee = chore_dict[Chore_Col_Name.assignee.value]
        status = Status[chore_dict[Chore_Col_Name.status.value]]

        return cls(name, choreid, description, request_date, due_date, requester, assignee, status)

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

    def get_chore_request_model(self) -> ChoreCreateRequest:
        assigned_to = None if not self.assignee else self.assignee.full_name
        return ChoreCreateRequest(name=self.name,
                                  description=self.description,
                                  assigned_to=assigned_to)
    
    def get_chore_response_model(self) -> ChoreCreateRequest:
        assigned_to = None if not self.assignee else self.assignee.full_name
        return ChoreCreateRequest(name=self.name,
                                  description=self.description,
                                  assigned_to=assigned_to,
                                  status=self.status.name)

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
        name: Name of the chore.
        description: Description of the chore.
        assigned_to: Username of the user assigned to the chore.
        status: Current status of the chore.
    """
    name: str
    description: str
    assigned_to: Optional[str]
    status: str
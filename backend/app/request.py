from enum import Enum
from typing import Union
from pydantic import BaseModel

"""
Module for managing chore request operations.

Contributors: Gilligan Berlinski
"""

REQUEST_TABLE_NAME = "requests"
REQUEST_VIEW = "requests_view"

class Request_Col_Name(Enum):
    requestid = "requestid"
    chorerequestid = "chore_request_id"
    requestedassigneeid = "requested_assignee_id"
    requeststatus = "request_status"
    createdat = "created_at"
    respondedat = "responded_at"

class Request_View_Col_Name(Enum):
    chorename = "chore_name"
    assigneename = "assignee_username"
    requestername = "requester_username"
    requesterid = "requester_userid"

class RequestStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class RequestCreateRequest(BaseModel):
    householdid: int
    requester_userid: int
    requested_assignee_userid: int
    requested_choreid: int

class RequestResponse(BaseModel):
    requestid: int
    requester_userid: int
    requester_name: str
    requested_assignee_userid: int
    requested_assignee_name: str
    requested_choreid: int
    requested_chore_name: str
    request_status: RequestStatus
    created_at: str
    responded_at: Union[str, None]

class RequestUpdateRequest(BaseModel):
    updated_status: RequestStatus
    responded_at: str

def create_RequestResponse(data: dict) -> RequestResponse:
    return RequestResponse(
        requestid=data[Request_Col_Name.requestid.value],
        requester_userid=data[Request_View_Col_Name.requesterid.value],
        requester_name=data[Request_View_Col_Name.requestername.value],
        requested_assignee_userid=data[Request_Col_Name.requestedassigneeid.value],
        requested_assignee_name=data[Request_View_Col_Name.assigneename.value],
        requested_choreid=data[Request_Col_Name.chorerequestid.value],
        requested_chore_name=data[Request_View_Col_Name.chorename.value],
        request_status=data[Request_Col_Name.requeststatus.value],
        created_at=data[Request_Col_Name.createdat.value],
        responded_at=data[Request_Col_Name.respondedat.value]
    )
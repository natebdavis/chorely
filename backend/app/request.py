from enum import Enum
from pydantic import BaseModel

"""
Module for managing chore request operations.

Contributors: Gilligan Berlinski
"""

REQUEST_TABLE_NAME = "requests"

class Request_Col_Name(Enum):
    requestid = "requestid"
    chorerequestid = "chore_request_id"
    requestedassigneeid = "requested_assignee_id"
    requeststatus = "request_status"

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
    requested_assignee_userid: int
    requested_choreid: int
    request_status: RequestStatus

class RequestStatusUpdateRequest(BaseModel):
    updated_status: RequestStatus


def create_RequestResponse(data: dict) -> RequestResponse:
    return RequestResponse(
        requestid=data[Request_Col_Name.requestid.value],
        requested_assignee_userid=data[Request_Col_Name.requestedassigneeid.value],
        requested_choreid=data[Request_Col_Name.requestedassigneeid.value],
        request_status=data[Request_Col_Name.requeststatus.value]
    )
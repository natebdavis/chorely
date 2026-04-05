from enum import Enum
from typing import Union
from pydantic import BaseModel


"""
Module for managing household invite operations.

Contributors: Edmund Krajewski
"""

INVITE_TABLE_NAME = "household_invites"


class Invite_Col_Name(Enum):
    inviteid = "inviteid"
    householdid = "householdid"
    inviter_userid = "inviter_userid"
    invitee_userid = "invitee_userid"
    status = "status"
    created_at = "created_at"
    responded_at = "responded_at"


class InviteStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    CANCELED = "CANCELED"


class InviteCreateRequest(BaseModel):
    householdid: int
    inviter_userid: int
    invitee_userid: int
    status: str
    created_at: str


class InviteResponse(BaseModel):
    inviteid: int
    householdid: int
    inviter_userid: int
    invitee_userid: int
    status: str
    created_at: str
    responded_at: Union[str, None] = None


class InviteStatusUpdateRequest(BaseModel):
    status: str
    responded_at: str


def create_InviteResponse(data: dict) -> InviteResponse:
    return InviteResponse(
        inviteid=data[Invite_Col_Name.inviteid.value],
        householdid=data[Invite_Col_Name.householdid.value],
        inviter_userid=data[Invite_Col_Name.inviter_userid.value],
        invitee_userid=data[Invite_Col_Name.invitee_userid.value],
        status=data[Invite_Col_Name.status.value],
        created_at=data[Invite_Col_Name.created_at.value],
        responded_at=data.get(Invite_Col_Name.responded_at.value),
    )
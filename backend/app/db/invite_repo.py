from collections.abc import Iterable
from typing import Union

from supabase import Client

from app.db.client import get_client
from app.invite import (
    INVITE_TABLE_NAME,
    Invite_Col_Name,
    InviteCreateRequest,
    InviteResponse,
    InviteStatus,
    create_InviteResponse,
)

first = 0


def get_invite(
    inviteid: int,
    client: Union[Client, None] = None,
) -> Union[InviteResponse, None]:
    if client is None:
        client = get_client()

    response = (
        client
        .table(INVITE_TABLE_NAME)
        .select("*")
        .eq(Invite_Col_Name.inviteid.value, inviteid)
        .execute()
    )

    data = response.data
    if not data:
        return None

    return create_InviteResponse(data[first])


def get_user_invites(
    userid: int,
    client: Union[Client, None] = None,
) -> Iterable[InviteResponse]:
    if client is None:
        client = get_client()

    response = (
        client
        .table(INVITE_TABLE_NAME)
        .select("*")
        .eq(Invite_Col_Name.invitee_userid.value, userid)
        .order(Invite_Col_Name.created_at.value, desc=True)
        .execute()
    )

    data = response.data or []
    return [create_InviteResponse(row) for row in data]


def get_user_pending_invites(
    userid: int,
    client: Union[Client, None] = None,
) -> Iterable[InviteResponse]:
    if client is None:
        client = get_client()

    response = (
        client
        .table(INVITE_TABLE_NAME)
        .select("*")
        .eq(Invite_Col_Name.invitee_userid.value, userid)
        .eq(Invite_Col_Name.status.value, InviteStatus.PENDING.value)
        .order(Invite_Col_Name.created_at.value, desc=True)
        .execute()
    )

    data = response.data or []
    return [create_InviteResponse(row) for row in data]


def get_outgoing_pending_invites(
    inviter_userid: int,
    client: Union[Client, None] = None,
) -> Iterable[InviteResponse]:
    if client is None:
        client = get_client()

    response = (
        client
        .table(INVITE_TABLE_NAME)
        .select("*")
        .eq(Invite_Col_Name.inviter_userid.value, inviter_userid)
        .eq(Invite_Col_Name.status.value, InviteStatus.PENDING.value)
        .order(Invite_Col_Name.created_at.value, desc=True)
        .execute()
    )

    data = response.data or []
    return [create_InviteResponse(row) for row in data]


def get_pending_invite_for_household_user(
    householdid: int,
    invitee_userid: int,
    client: Union[Client, None] = None,
) -> Union[InviteResponse, None]:
    if client is None:
        client = get_client()

    response = (
        client
        .table(INVITE_TABLE_NAME)
        .select("*")
        .eq(Invite_Col_Name.householdid.value, householdid)
        .eq(Invite_Col_Name.invitee_userid.value, invitee_userid)
        .eq(Invite_Col_Name.status.value, InviteStatus.PENDING.value)
        .limit(1)
        .execute()
    )

    data = response.data
    if not data:
        return None

    return create_InviteResponse(data[first])


def create_invite(
    invite: InviteCreateRequest,
    client: Union[Client, None] = None,
) -> Union[InviteResponse, None]:
    if client is None:
        client = get_client()

    data = {
        Invite_Col_Name.householdid.value: invite.householdid,
        Invite_Col_Name.inviter_userid.value: invite.inviter_userid,
        Invite_Col_Name.invitee_userid.value: invite.invitee_userid,
        Invite_Col_Name.status.value: invite.status,
        Invite_Col_Name.created_at.value: invite.created_at,
    }

    response = client.table(INVITE_TABLE_NAME).insert(data).execute()
    rows = response.data

    if not rows:
        return None

    return create_InviteResponse(rows[first])


def update_invite_status(
    inviteid: int,
    status: str,
    responded_at: str,
    client: Union[Client, None] = None,
) -> Union[InviteResponse, None]:
    if client is None:
        client = get_client()

    data = {
        Invite_Col_Name.status.value: status,
        Invite_Col_Name.responded_at.value: responded_at,
    }

    response = (
        client
        .table(INVITE_TABLE_NAME)
        .update(data)
        .eq(Invite_Col_Name.inviteid.value, inviteid)
        .execute()
    )

    rows = response.data
    if not rows:
        return None

    return create_InviteResponse(rows[first])


def cancel_pending_invites_for_user(
    invitee_userid: int,
    responded_at: str,
    exclude_inviteid: Union[int, None] = None,
    client: Union[Client, None] = None,
) -> Iterable[InviteResponse]:
    if client is None:
        client = get_client()

    query = (
        client
        .table(INVITE_TABLE_NAME)
        .update({
            Invite_Col_Name.status.value: InviteStatus.CANCELED.value,
            Invite_Col_Name.responded_at.value: responded_at,
        })
        .eq(Invite_Col_Name.invitee_userid.value, invitee_userid)
        .eq(Invite_Col_Name.status.value, InviteStatus.PENDING.value)
    )

    if exclude_inviteid is not None:
        query = query.neq(Invite_Col_Name.inviteid.value, exclude_inviteid)

    response = query.execute()
    rows = response.data or []

    return [create_InviteResponse(row) for row in rows]
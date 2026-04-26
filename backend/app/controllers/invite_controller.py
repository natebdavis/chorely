"""
Module for managing Invite Controller operations.
Handles HTTP requests related to household invites and exposes API endpoints
for retrieving, accepting, declining, and canceling invites.

Contributors: Edmund Krajewski
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import datetime as DT

from app.database import (
    cancel_pending_invites_for_user,
    get_current_user,
    get_invite,
    get_outgoing_pending_invites,
    get_user_pending_invites,
    get_user_invites,
    update_invite_status,
    join_household,
    get_household_member_count,
    household_exists,
    get_user,
)
from app.invite import InviteResponse, InviteStatus
from app.notification import NotificationCreateRequest, NotificationType
from app.db.notification_repo import create_notification
from app.user import UserResponse, get_full_name

router = APIRouter(prefix="/invites", tags=["invites"])


@router.get("", response_model=List[InviteResponse])
def get_my_pending_invites(
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Retrieve all pending invites for the current user.
    """
    return list(get_user_pending_invites(current_user.userid))


@router.get("/outgoing", response_model=List[InviteResponse])
def get_my_outgoing_pending_invites(
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Retrieve all outgoing pending invites for the current user.
    """
    return list(get_outgoing_pending_invites(current_user.userid))


@router.get("/history", response_model=List[InviteResponse])
def get_my_invite_history(
    current_user: UserResponse = Depends(get_current_user),
):
    return list(get_user_invites(current_user.userid))


@router.post("/{inviteid}/accept")
def accept_invite(
    inviteid: int,
    current_user: UserResponse = Depends(get_current_user),
):
    """
     Accept a household invite.
     This will add the user to the household, update the invite status to accepted, and cancel any other pending invites for the user.
     
     Raises:
     - HTTPException 400: If the invite is no longer pending, user already belongs to a household, or household has reached maximum member limit.
     - HTTPException 403: If the current user is not the invitee.
     - HTTPException 404: If the invite or household is not found.
     - HTTPException 500: If failed to join household or update invite status.
     """
    invite = get_invite(inviteid)

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found",
        )

    if invite.invitee_userid != current_user.userid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to respond to this invite",
        )

    if invite.status != InviteStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite is no longer pending",
        )

    if current_user.householdid is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already belongs to a household",
        )

    if not household_exists(invite.householdid):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Household no longer exists",
        )

    if get_household_member_count(invite.householdid) >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Household has reached maximum member limit",
        )

    joined_user = join_household(current_user.userid, invite.householdid)

    if not joined_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join household",
        )

    now = DT.datetime.now().isoformat()

    updated = update_invite_status(
        inviteid=inviteid,
        status=InviteStatus.ACCEPTED.value,
        responded_at=now,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update invite status",
        )

    cancel_pending_invites_for_user(
        invitee_userid=current_user.userid,
        responded_at=now,
        exclude_inviteid=inviteid,
    )

    inviter = get_user(userid=invite.inviter_userid)
    if inviter:
        create_notification(
            NotificationCreateRequest(
                userid=invite.inviter_userid,
                type=NotificationType.INVITE_ACCEPTED.value,
                title="Invite Accepted",
                message=f"{get_full_name(current_user)} accepted your household invite",
                reference_id=invite.inviteid,
                time=now,
                is_read=False,
            )
        )

    return {
        "message": "Invite accepted successfully",
        "householdid": invite.householdid,
    }


@router.post("/{inviteid}/decline")
def decline_invite(
    inviteid: int,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Decline a household invite.
    
    Raises:
    - HTTPException 400: If the invite is no longer pending.
    - HTTPException 403: If the current user is not the invitee.
    - HTTPException 404: If the invite is not found.
    - HTTPException 500: If failed to update invite status.
    """
    invite = get_invite(inviteid)

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found",
        )

    if invite.invitee_userid != current_user.userid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to respond to this invite",
        )

    if invite.status != InviteStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite is no longer pending",
        )

    now = DT.datetime.now().isoformat()

    updated = update_invite_status(
        inviteid=inviteid,
        status=InviteStatus.DECLINED.value,
        responded_at=now,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update invite status",
        )

    inviter = get_user(userid=invite.inviter_userid)
    if inviter:
        create_notification(
            NotificationCreateRequest(
                userid=invite.inviter_userid,
                type=NotificationType.INVITE_DECLINED.value,
                title="Invite Declined",
                message=f"{get_full_name(current_user)} declined your household invite",
                reference_id=invite.inviteid,
                time=now,
                is_read=False,
            )
        )

    return {"message": "Invite declined successfully"}


@router.post("/{inviteid}/cancel")
def cancel_invite(
    inviteid: int,
    current_user: UserResponse = Depends(get_current_user),
):
    """Cancel a household invite.
    
    Raises:
    - HTTPException 400: If the invite is no longer pending.
    - HTTPException 403: If the current user is not the inviter.
    - HTTPException 404: If the invite is not found.
    - HTTPException 500: If failed to cancel invite.
    """
    invite = get_invite(inviteid)

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found",
        )

    if invite.inviter_userid != current_user.userid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this invite",
        )

    if invite.status != InviteStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite is no longer pending",
        )

    now = DT.datetime.now().isoformat()

    updated = update_invite_status(
        inviteid=inviteid,
        status=InviteStatus.CANCELED.value,
        responded_at=now,
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel invite",
        )

    if invite.invitee_userid != current_user.userid:
        create_notification(
            NotificationCreateRequest(
                userid=invite.invitee_userid,
                type=NotificationType.INVITE_DECLINED.value,
                title="Invite Canceled",
                message=f"{get_full_name(current_user)} canceled a household invite",
                reference_id=invite.inviteid,
                time=now,
                is_read=False,
            )
        )

    return {"message": "Invite canceled successfully"}
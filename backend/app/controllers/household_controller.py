"""
Module for managing Household Controller operations.
Handles HTTP requests related to households and exposes API endpoints
for retrieving household information, creating households, inviting users to households, leaving households, removing members from households, and transferring household ownership.

Contributors: Edmund Krajewski, Gilligan Berlinski
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List
import datetime as DT

from app.household import (
    HouseholdRemoveMemberRequest,
    HouseholdResponse,
    HouseholdInviteRequest,
    HouseholdTransferOwnershipRequest,
)
from app.invite import InviteCreateRequest, InviteStatus
from app.notification import NotificationCreateRequest, NotificationType
from app.db.notification_repo import create_notification
from app.database import (
    get_household_member_count,
    get_current_user,
    get_householdid,
    join_household,
    create_household_db,
    get_users,
    leave_household,
    get_user,
    create_invite,
    get_pending_invite_for_household_user,
    get_owner_householdid,
    transfer_household_ownership,
    delete_household_if_empty
)
from app.user import UserResponse, get_full_name

router = APIRouter(tags=["households"], prefix="/households")
""" API router for household-related endpoints."""


@router.get("/members", response_model=List[UserResponse])
def get_household_users(current_user: UserResponse = Depends(get_current_user)):
    """
    Get all users in the current user's household.
    
    Raises:
    - HTTPException 404: If the user is not part of a household or no users are found in the household.
    """
    householdid = current_user.householdid

    if householdid is None:
        raise HTTPException(
            status_code=404,
            detail="User has not joined a household",
        )

    users = get_users(householdid)

    if not users:
        raise HTTPException(
            status_code=404,
            detail="No users in household found",
        )

    return list(users)


@router.get("", response_model=HouseholdResponse)
def get_household(current_user: UserResponse = Depends(get_current_user)):
    """
    Get the current user's household information, including householdid and member count.

     Raises:
     - HTTPException 404: If the user is not part of a household.
     """
    householdid = current_user.householdid

    if householdid is None:
        raise HTTPException(
            status_code=404,
            detail="User has not joined a household",
        )

    return HouseholdResponse(
        householdid=householdid,
        member_count=get_household_member_count(householdid),
    )


@router.post("", response_model=HouseholdResponse)
def create_household(current_user: UserResponse = Depends(get_current_user)):
    """ Create a new household and add the current user as the owner.

     Raises:
     - HTTPException 400: If the user is already part of a household.
     - HTTPException 500: If failed to create household or add user to household.
     """
    householdid = get_householdid(current_user.userid)

    if householdid is not None:
        raise HTTPException(
            status_code=400,
            detail="User is already apart of an existing household.",
        )

    new_household = create_household_db()

    if not new_household:
        raise HTTPException(
            status_code=500,
            detail="Failed to create household",
        )

    joined_user = join_household(userid=current_user.userid, householdid=new_household.householdid, is_owner=True)

    if not joined_user:
        raise HTTPException(
            status_code=500,
            detail="Failed to add user to newly created household",
        )

    return HouseholdResponse(
        householdid=new_household.householdid,
        member_count=1,
    )


def _send_household_invite(
    request: HouseholdInviteRequest,
    current_user: UserResponse,
):
    current_householdid = get_householdid(userid=current_user.userid)

    if current_householdid is None:
        raise HTTPException(
            status_code=400,
            detail="User must be in a household to invite others",
        )

    if current_user.userid == request.userid:
        raise HTTPException(
            status_code=400,
            detail="User cannot invite themselves",
        )

    member_count = get_household_member_count(current_householdid)
    if member_count >= 10:
        raise HTTPException(
            status_code=400,
            detail="Household has reached maximum member limit",
        )

    user = get_user(userid=request.userid)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user.householdid == current_householdid:
        raise HTTPException(
            status_code=400,
            detail="User already in this household",
        )

    if user.householdid is not None:
        raise HTTPException(
            status_code=400,
            detail="User already belongs to another household",
        )

    existing_invite = get_pending_invite_for_household_user(
        householdid=current_householdid,
        invitee_userid=request.userid,
    )

    if existing_invite:
        raise HTTPException(
            status_code=409,
            detail="A pending invite already exists for this user and household",
        )

    now = DT.datetime.now().isoformat()

    invite_payload = InviteCreateRequest(
        householdid=current_householdid,
        inviter_userid=current_user.userid,
        invitee_userid=request.userid,
        status=InviteStatus.PENDING.value,
        created_at=now,
    )

    created_invite = create_invite(invite_payload)

    if not created_invite:
        raise HTTPException(
            status_code=500,
            detail="Failed to create invite",
        )

    created_notification = create_notification(
        NotificationCreateRequest(
            userid=request.userid,
            type=NotificationType.INVITE.value,
            title="Household Invite",
            message=f"{get_full_name(current_user)} invited you to join household {current_householdid}",
            reference_id=created_invite.inviteid,
            time=now,
            is_read=False,
        )
    )

    if not created_notification:
        raise HTTPException(
            status_code=500,
            detail="Invite created but notification failed",
        )

    return {
        "message": "Invite sent successfully",
        "inviteid": created_invite.inviteid,
    }


@router.post("/invite")
def invite_to_household(
    request: HouseholdInviteRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """ Invite a user to the current user's household.
    
    Raises:
    - HTTPException 400: If the user is not part of a household or the invite is invalid.
    - HTTPException 404: If the user to invite is not found.
    - HTTPException 409: If a pending invite already exists for this user and household.
    - HTTPException 500: If failed to create invite or notification.
    """
    return _send_household_invite(request, current_user)


@router.post("/join")
def join_household_route(
    request: HouseholdInviteRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """ 
    Join a household using an invite.

    Raises:
    - HTTPException 400: If the user is already part of a household or the invite is invalid.
    - HTTPException 404: If the user to invite is not found.
    - HTTPException 409: If a pending invite already exists for this user and household.
    - HTTPException 500: If failed to create invite or notification.
    """
    return _send_household_invite(request, current_user)


@router.delete("/leave")
def leave_household_route(
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Leave the current user's household.

    Raises:
     - HTTPException 400: If the user is not part of a household.
     - HTTPException 500: If failed to leave household.
     """
    user = get_user(userid=current_user.userid)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user.householdid is None:
        raise HTTPException(
            status_code=400,
            detail="User is not part of a household",
        )
    
    user_owned_householdid = get_owner_householdid(current_user.userid)
    owner_leaving = False

    if user_owned_householdid:
        member_count = get_household_member_count(current_user.householdid)
        if member_count > 1 and user_owned_householdid == current_user.householdid:
            raise HTTPException(
                status_code=403,
                detail="Household owner can not leave household of two or more members without transferring ownership.",
            )
        owner_leaving = True

    left_user = leave_household(current_user.userid)

    if not left_user:
        raise HTTPException(
            status_code=500,
            detail="Failed to leave household",
        )
    
    if owner_leaving:
        delete_household_if_empty(user_owned_householdid)
    
    return {"message": "User left household successfully"}

@router.delete("/remove")
def remove_member_from_household_route(
    request: HouseholdRemoveMemberRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Remove a member from the current user's household. Only the household owner can remove members other than themselves.

    Raises:
    - HTTPException 400: If the user is not part of a household, the request is invalid, or the user tries to remove themselves.
    - HTTPException 403: If the current user is not the household owner or tries to remove a user that is not in their household.
    - HTTPException 404: If the user to remove is not found.
    - HTTPException 500: If failed to remove user from household.
    """
    if request.userid == current_user.userid:
        raise HTTPException(
            status_code=400,
            detail="User cannot remove themselves from the household, must leave instead.",
        )

    householdid = current_user.householdid

    if householdid is None:
        raise HTTPException(
            status_code=400,
            detail="User is not part of a household",
        )
    
    user_owned_householdid = get_owner_householdid(current_user.userid)

    if user_owned_householdid is None or user_owned_householdid != householdid:
        raise HTTPException(
            status_code=403,
            detail="Only the household owner can remove members",
        )

    householdid_request = get_householdid(request.userid)

    if householdid_request is None or householdid_request != householdid:
        raise HTTPException(
            status_code=403,
            detail="User is not a member of your household",
        )
    
    removed_user = leave_household(request.userid)

    if not removed_user:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to remove user from household",
        )
    
    return {"message": "User removed from household successfully"}

@router.patch("/transfer-ownership")
def transfer_household_ownership_route(
    request: HouseholdTransferOwnershipRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Transfer household ownership to another member of the household.
    
    Raises:
    - HTTPException 400: If the user is not part of a household, the request is invalid, or the user tries to transfer ownership to themselves.
    - HTTPException 403: If the current user is not the household owner or tries to transfer ownership to a user that is not in their household.
    - HTTPException 404: If the new owner user is not found.
    - HTTPException 500: If failed to transfer household ownership.
    """
    if request.new_owner_userid == current_user.userid:
        raise HTTPException(
            status_code=400,
            detail="User cannot transfer ownership to themselves",
        )

    householdid = current_user.householdid

    if householdid is None:
        raise HTTPException(
            status_code=400,
            detail="User is not part of a household",
        )

    user_owned_householdid = get_owner_householdid(current_user.userid)

    if user_owned_householdid is None or user_owned_householdid != householdid:
        raise HTTPException(
            status_code=403,
            detail="Only the household owner can transfer ownership",
        )

    success = transfer_household_ownership(householdid, request.new_owner_userid)

    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to transfer household ownership",
        )

    return {"message": "Household ownership transferred successfully"}

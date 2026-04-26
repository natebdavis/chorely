"""
Module for managing Request Controller operations.
Contributors: Gilligan Berlinski
"""
from typing import Iterable
import datetime as DT

from fastapi import APIRouter, HTTPException, Depends, status
from app.chore import Status as ChoreStatus
from app.user import UserResponse
from app.database import get_current_user, get_user, get_user_requests, get_outgoing_pending_requests, create_request, get_request, update_request, get_requester, update_chore, create_notification
from app.request import RequestResponse, RequestCreateRequest, RequestUpdateRequest, RequestStatus
from app.db.chore_repo import get_chore
from app.notification import NotificationCreateRequest, NotificationType


router = APIRouter(prefix="/requests", tags=["requests"])
""" API router for chore request-related endpoints."""

@router.get("", response_model=Iterable[RequestResponse])
def get_my_pending_requests(
    current_user: UserResponse = Depends(get_current_user),
):
    """Get all pending requests for the current user."""

    response = get_user_requests(current_user.userid)

    if response is None:
        return []
    else:
        return response

@router.get("/outgoing", response_model=Iterable[RequestResponse])
def get_my_outgoing_pending_requests(
    current_user: UserResponse = Depends(get_current_user),
):
    """Get all outgoing pending requests for the current user."""

    response = get_outgoing_pending_requests(current_user.userid)

    if response is None:
        return []
    else:
        return response

@router.post("", response_model=RequestResponse)
def create_chore_request(request: RequestCreateRequest, current_user: UserResponse = Depends(get_current_user)):

    """Create a chore request for a specified chore and assignee user.

    Raises:
    - HTTPException 400: If the request is invalid, assignee user is not in the same household as the requester, or the chore is not found.
    - HTTPException 404: If the requested assignee or chore is not found.
    """

    requested_assignee = get_user(userid=request.requested_assignee_userid)
    if not requested_assignee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested assignee user not found",
        )
    
    if current_user.householdid != request.householdid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not in the same household as the request",
        )
    
    if requested_assignee.householdid != request.householdid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested assignee is not in the same household as the requester user",
        )
    
    chore = get_chore(choreid=request.requested_choreid)

    if chore.assignee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested chore is already assigned to another user",
        )

    try:    
        created_request = create_request(request)

        if created_request:
            now = DT.datetime.now().isoformat()
            create_notification(
            NotificationCreateRequest(
                userid=requested_assignee.userid,
                type=NotificationType.CHORE_REQUESTED.value,
                title="Chore Requested",
                message=f"{current_user.username} requested a chore from you: {chore.name}",
                reference_id=created_request.requestid,
                time=now,
                is_read=False,)
            )
        return created_request
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
@router.post("/{requestid}/accept")
def accept_request(
    requestid: int,
    current_user: UserResponse = Depends(get_current_user),
):
    """Accept a chore request, updating the request status and chore assignee accordingly.

    Raises:
    - HTTPException 400: The request has already been responded to, or the requested chore is not found.
    - HTTPException 403: If the current user is not the requested assignee for the request.
    - HTTPException 404: If the request or requested chore is not found.
    - HTTPException 500: If updating the request status or chore assignee fails.
    """

    request = get_request(requestid)
    chore = get_chore(choreid=request.requested_choreid)

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found",
        )
    if request.request_status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request has already been responded to",
        )
    if request.requested_assignee_userid != current_user.userid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to respond to this request",
        )
    
    if not chore:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested chore not found",
        )
    
    if chore.assignee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested chore has already assigned to another user",
        )
    
    now = DT.datetime.now().isoformat()
    
    response = update_request(requestid, RequestUpdateRequest(updated_status=RequestStatus.ACCEPTED.value, responded_at=now))

    if not response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update request status",
        )
    
    response = update_chore(
        householdid=current_user.householdid,
        choreid=chore.choreid,
        assignee_id=current_user.userid,
        status=ChoreStatus.IN_PROGRESS.name,
        status_provided=True,
        assignee_provided=True,
        priority=chore.priority,
        location=chore.location,
        ctype=chore.ctype
    )

    if not response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chore assignee and status",
        )
    
    requester = get_requester(choreid=request.requested_choreid)

    if requester:
        create_notification(
            NotificationCreateRequest(
                userid=requester.userid,
                type=NotificationType.CHORE_ASSIGNED.value,
                title="Chore Request Accepted",
                message=f"{current_user.username} accepted your chore request for chore: {chore.name}",
                reference_id=requestid,
                time=now,
                is_read=False,
            )
        )

    return {"message": "Chore accepted successfully", "choreid": chore.choreid,}


@router.post("/{requestid}/decline")
def reject_request(
    requestid: int,
    current_user: UserResponse = Depends(get_current_user),
):
    """Rejects a chore request, updating the request status.
    
    Raises:
    - HTTPException 400: The request has already been responded to, or the requested chore is not found.
    - HTTPException 403: If the current user is not the requested assignee for the request.
    - HTTPException 404: If the request or requested chore is not found.
    - HTTPException 500: If updating the request status or chore assignee fails."""

    request = get_request(requestid)
    chore = get_chore(choreid=request.requested_choreid)

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found",
        )
    if request.request_status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request has already been responded to",
        )
    if request.requested_assignee_userid != current_user.userid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to respond to this request",
        )
    
    if not chore:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested chore not found",
        )
    
    now = DT.datetime.now().isoformat()

    response = update_request(requestid, RequestUpdateRequest(updated_status=RequestStatus.REJECTED, responded_at=now))

    if not response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update request status",
        )
    
    requester = get_requester(choreid=request.requested_choreid)

    if requester:
        create_notification(
            NotificationCreateRequest(
                userid=requester.userid,
                type=NotificationType.CHORE_REJECTED.value,
                title="Chore Request Rejected",
                message=f"{current_user.username} rejected your chore request for chore: {chore.name}",
                reference_id=requestid,
                time=now,
                is_read=False,
            )
        )

    return {"message": "Chore rejected successfully", "choreid": chore.choreid,}
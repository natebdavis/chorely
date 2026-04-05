from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from app.notification import NotificationCreateRequest, NotificationResponse
from app.database import (
    get_notifications as db_get_notifications,
    get_notification as db_get_notification,
    add_notification as db_add_notification,
    mark_notification_read as db_mark_notification_read,
    remove_notification as db_remove_notification,
    get_current_user,
)
from app.user import UserResponse

"""
Module for managing Notification Controller operations.
Handles HTTP requests related to Notifications and exposes API endpoints
for creating, retrieving, updating, and deleting notifications.
"""

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=List[NotificationResponse])
def get_notifications(current_user: UserResponse = Depends(get_current_user)):
    """
    Retrieve all notifications for the current user.
    """
    return list(db_get_notifications(current_user.userid))


@router.get("/{notificationid}", response_model=NotificationResponse)
def get_notification(
    notificationid: int,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Retrieve a single notification by notificationid.
    """
    notification = db_get_notification(notificationid)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    if notification.userid != current_user.userid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this notification",
        )

    return notification


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(
    payload: NotificationCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Create a new notification.
    """
    created = db_add_notification(payload)

    if not created:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create notification",
        )

    return created


@router.patch("/{notificationid}/read", response_model=NotificationResponse)
def mark_notification_read(
    notificationid: int,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Mark a notification as read.
    """
    notification = db_get_notification(notificationid)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    if notification.userid != current_user.userid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this notification",
        )

    updated = db_mark_notification_read(notificationid)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notification as read",
        )

    return updated


@router.delete("/{notificationid}", status_code=status.HTTP_200_OK)
def delete_notification(
    notificationid: int,
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Delete a notification by notificationid.
    """
    notification = db_get_notification(notificationid)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    if notification.userid != current_user.userid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this notification",
        )

    deleted = db_remove_notification(notificationid)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return {"message": "Notification deleted successfully"}
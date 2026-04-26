"""
Module for managing Notification Controller operations.
Handles HTTP requests related to Notifications and exposes API endpoints
for creating, retrieving, updating, and deleting notifications.

Contributors: Edmund Krajewski
"""
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

router = APIRouter(prefix="/notifications", tags=["notifications"])
""" API router for notification-related endpoints."""


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

    Raises:
    - HTTPException 403: If the current user is not the owner of the notification.
    - HTTPException 404: If the notification is not found.
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

    Raises:
    - HTTPException 500: If failed to create notification.

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

    Raises:
    - HTTPException 404: If the notification is not found.
    - HTTPException 403: If the current user is not the owner of the notification.
    - HTTPException 500: If failed to mark the notification as read.
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

    Raises:
    - HTTPException 404: If the notification is not found.
    - HTTPException 403: If the current user is not the owner of the notification.
    - HTTPException 500: If failed to delete the notification.
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
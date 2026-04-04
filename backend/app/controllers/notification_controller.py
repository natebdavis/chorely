from fastapi import APIRouter, HTTPException, status
from typing import List

from app.notification import NotificationCreateRequest, NotificationResponse
from app.database import (
    get_notifications as db_get_notifications,
    get_notification as db_get_notification,
    add_notification as db_add_notification,
    remove_notification as db_remove_notification,
)

"""
Module for managing Notification Controller operations.
Handles HTTP requests related to Notifications and exposes API endpoints
for creating, retrieving, and deleting notifications.

Contributors: Edmund Krajewski
"""

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=List[NotificationResponse])
def get_notifications():
    """
    Retrieve all notifications.
    """
    notifications = db_get_notifications()
    return notifications or []


@router.get("/{notificationid}", response_model=NotificationResponse)
def get_notification(notificationid: int):
    """
    Retrieve a single notification by notificationid.
    """
    notification = db_get_notification(notificationid)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return notification


@router.post("", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
def create_notification(payload: NotificationCreateRequest):
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


@router.delete("/{notificationid}", status_code=status.HTTP_200_OK)
def delete_notification(notificationid: int):
    """
    Delete a notification by notificationid.
    """
    deleted = db_remove_notification(notificationid)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    return {"message": "Notification deleted successfully"}
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

"""
Module for managing Notification Controller operations.
Handles HTTP requests related to Notifications and exposes API endpoints
for creating, retrieving, and deleting notifications.

Contributors: Edmund Krajewski
"""

router = APIRouter(tags=["notifications"])


class NotificationCreateRequest(BaseModel):
    """
    Request body schema for creating a new Notification.

    Inputs:
        notificationid: Unique identifier for the Notification.
        choreid: Identifier of the Chore associated with the Notification.
        time: Datetime string representing when the Notification should occur.

    Output:
        JSON body representing a Notification creation request.
    """
    notificationid: int
    choreid: int
    time: str


class NotificationResponse(BaseModel):
    """
    Response schema returned for Notification-related API requests.

    Outputs:
        notificationid: Unique identifier for the Notification.
        choreid: Identifier of the associated Chore.
        time: Datetime string representing when the Notification occurs.
    """
    notificationid: int
    choreid: int
    time: str


class TempNotification(BaseModel):
    """
    Temporary Notification schema used for in-memory backend testing.

    Inputs:
        notificationid: Unique identifier for the Notification.
        choreid: Identifier of the associated Chore.
        time: Datetime string representing when the Notification occurs.

    Output:
        Temporary Notification object for testing storage and retrieval.
    """
    notificationid: int
    choreid: int
    time: str


"""
Temporary in-memory storage for Notifications.

This acts as a placeholder until persistent database-backed
Notification storage is implemented.
"""
fake_notifications: List[TempNotification] = [
    TempNotification(notificationid=1, choreid=1, time="2026-03-15T18:00:00"),
    TempNotification(notificationid=2, choreid=2, time="2026-03-16T12:00:00"),
]


@router.get("/notifications", response_model=List[NotificationResponse])
def get_notifications():
    """
    Retrieve all Notifications currently stored.

    Inputs:
        None

    Outputs:
        List of all Notifications currently in the system.
    """
    return [
        NotificationResponse(
            notificationid=notification.notificationid,
            choreid=notification.choreid,
            time=notification.time,
        )
        for notification in fake_notifications
    ]


@router.get("/notifications/{notificationid}", response_model=NotificationResponse)
def get_notification(notificationid: int):
    """
    Retrieve a single Notification by notificationid.

    Inputs:
        notificationid: Unique identifier of the Notification to retrieve.

    Outputs:
        NotificationResponse for the requested Notification.

    Raises:
        HTTPException(404) if the Notification does not exist.
    """
    for notification in fake_notifications:
        if notification.notificationid == notificationid:
            return NotificationResponse(
                notificationid=notification.notificationid,
                choreid=notification.choreid,
                time=notification.time,
            )

    raise HTTPException(status_code=404, detail="Notification not found")


@router.post("/notifications", response_model=NotificationResponse)
def create_notification(request: NotificationCreateRequest):
    """
    Create a new Notification.

    Inputs:
        request: NotificationCreateRequest containing the new Notification data.

    Outputs:
        NotificationResponse representing the newly created Notification.

    Raises:
        HTTPException(400) if the Notification ID already exists.
    """
    for notification in fake_notifications:
        if notification.notificationid == request.notificationid:
            raise HTTPException(status_code=400, detail="Notification already exists")

    new_notification = TempNotification(
        notificationid=request.notificationid,
        choreid=request.choreid,
        time=request.time,
    )

    fake_notifications.append(new_notification)

    return NotificationResponse(
        notificationid=new_notification.notificationid,
        choreid=new_notification.choreid,
        time=new_notification.time,
    )


@router.delete("/notifications/{notificationid}")
def delete_notification(notificationid: int):
    """
    Delete a Notification by notificationid.

    Inputs:
        notificationid: Unique identifier of the Notification to delete.

    Outputs:
        Success message if deletion succeeds.

    Raises:
        HTTPException(404) if the Notification does not exist.
    """
    for i, notification in enumerate(fake_notifications):
        if notification.notificationid == notificationid:
            fake_notifications.pop(i)
            return {"message": "Notification deleted successfully"}

    raise HTTPException(status_code=404, detail="Notification not found")
"""
Module for managing notifications.

Contributors: Edmund Krajewski
"""
from enum import Enum
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationType(str, Enum):
    """Enumeration of possible notification types."""
    INVITE = "INVITE"
    INVITE_ACCEPTED = "INVITE_ACCEPTED"
    INVITE_DECLINED = "INVITE_DECLINED"
    INVITE_CANCELED = "INVITE_CANCELED"

    CHORE_ASSIGNED = "CHORE_ASSIGNED"
    CHORE_UNASSIGNED = "CHORE_UNASSIGNED"
    CHORE_REJECTED = "CHORE_REJECTED"
    CHORE_COMPLETED = "CHORE_COMPLETED"
    CHORE_REQUESTED = "CHORE_REQUESTED"

    CHORE_DUE_SOON = "CHORE_DUE_SOON"
    CHORE_OVERDUE = "CHORE_OVERDUE"
    CHORE_DAILY_SUMMARY = "CHORE_DAILY_SUMMARY"


class Notification(BaseModel):
    """Data model representing a notification."""
    notificationid: Optional[int] = None
    userid: int
    type: str
    title: str
    message: str
    reference_id: Optional[int] = None
    time: datetime
    is_read: bool = False

    def to_dict(self):
        """Convert the Notification object to a dictionary for database insertion."""
        return {
            "userid": self.userid,
            "type": self.type,
            "title": self.title,
            "message": self.message,
            "reference_id": self.reference_id,
            "time": self.time.isoformat() if isinstance(self.time, datetime) else self.time,
            "is_read": self.is_read,
        }


class NotificationCreateRequest(BaseModel):
    """Request body schema for creating a new notification from the backend."""
    userid: int
    type: str
    title: str
    message: str
    reference_id: Optional[int] = None
    time: datetime
    is_read: bool = False


class NotificationResponse(BaseModel):
    """Response schema returned for notification-related API requests."""
    notificationid: Optional[int]
    userid: int
    type: str
    title: str
    message: str
    reference_id: Optional[int]
    time: datetime
    is_read: bool


def create_NotificationResponse(data: dict) -> NotificationResponse:
    """Helper function to create a NotificationResponse object from a database record dictionary."""
    return NotificationResponse(
        notificationid=data.get("notid"),
        userid=data["userid"],
        type=data["type"],
        title=data["title"],
        message=data["message"],
        reference_id=data.get("reference_id"),
        time=data["time"],
        is_read=data.get("is_read", False),
    )
from enum import Enum
from pydantic import BaseModel

"""
Module for managing Notification operations.
Contributors: Edmund Krajewski
"""

NOTIFICATION_TABLE_NAME = "notifications"


class Notification_Col_Name(Enum):
    notificationid = "notificationid"
    choreid = "choreid"
    time = "time"


class NotificationCreateRequest(BaseModel):
    """
    Request body schema for creating a new notification.
    """
    choreid: int
    time: str


class NotificationResponse(BaseModel):
    """
    Response schema returned for notification-related API requests.
    """
    notificationid: int
    choreid: int
    time: str


def create_NotificationResponse(data: dict) -> NotificationResponse:
    return NotificationResponse(
        notificationid=data[Notification_Col_Name.notificationid.value],
        choreid=data[Notification_Col_Name.choreid.value],
        time=data[Notification_Col_Name.time.value],
    )
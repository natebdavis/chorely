from collections.abc import Iterable
from typing import Union

from supabase import Client

from app.db.client import get_client
from app.notification import (
    NOTIFICATION_TABLE_NAME,
    Notification_Col_Name,
    NotificationCreateRequest,
    NotificationResponse,
    create_NotificationResponse,
)

"""
Module for notification-related database operations.

Contributors: Edmund Krajewski
"""

first = 0


def get_notifications(
    client: Union[Client, None] = None,
) -> Union[Iterable[NotificationResponse], None]:
    """
    Get all notifications.

    Output:
        An iterable of NotificationResponse objects, or None if none exist.
    """
    if client is None:
        client = get_client()

    response = client.table(NOTIFICATION_TABLE_NAME).select("*").execute()
    data = response.data

    if not data:
        return None

    return [create_NotificationResponse(row) for row in data]


def get_notification(
    notificationid: int,
    client: Union[Client, None] = None,
) -> Union[NotificationResponse, None]:
    """
    Get a single notification by notificationid.

    Output:
        A NotificationResponse matching the notificationid, or None if not found.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(NOTIFICATION_TABLE_NAME)
        .select("*")
        .eq(Notification_Col_Name.notificationid.value, notificationid)
        .execute()
    )

    data = response.data
    if not data:
        return None

    return create_NotificationResponse(data[first])


def add_notification(
    notification: NotificationCreateRequest,
    client: Union[Client, None] = None,
) -> Union[NotificationResponse, None]:
    """
    Add a notification to the database.

    Output:
        Inserted notification returned as NotificationResponse, or None if insert failed.
    """
    if client is None:
        client = get_client()

    data = {
        Notification_Col_Name.choreid.value: notification.choreid,
        Notification_Col_Name.time.value: notification.time,
    }

    response = client.table(NOTIFICATION_TABLE_NAME).insert(data).execute()
    rows = response.data

    if not rows:
        return None

    return create_NotificationResponse(rows[first])


def remove_notification(
    notificationid: int,
    client: Union[Client, None] = None,
) -> bool:
    """
    Remove a notification from the database.

    Output:
        True if the notification was deleted, False otherwise.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(NOTIFICATION_TABLE_NAME)
        .delete()
        .eq(Notification_Col_Name.notificationid.value, notificationid)
        .execute()
    )

    return bool(response.data)
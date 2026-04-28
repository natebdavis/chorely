"""
Module for notification database operations.
Contributors: Edmund Krajewski
"""
from supabase import Client
from typing import Optional, List

from app.db.client import get_client
from app.notification import (
    Notification,
    NotificationResponse,
    NotificationCreateRequest,
    create_NotificationResponse,
)


def get_notifications(userid: int, client: Optional[Client] = None) -> List[NotificationResponse]:
    """
    Get all notifications for a user, ordered by time in descending order.
    
    Output:
        A list of NotificationResponse objects for the user.
    """
    if client is None:
        client = get_client()

    response = (
        client.table("notifications")
        .select("*")
        .eq("userid", userid)
        .order("time", desc=True)
        .execute()
    )

    data = response.data or []
    return [create_NotificationResponse(row) for row in data]


def get_notification(notificationid: int, client: Optional[Client] = None) -> Optional[NotificationResponse]:
    """
    Get a notification by its notificationid.
    
    Output:
        A NotificationResponse object if the notification exists, or None if it does not exist.
    """
    if client is None:
        client = get_client()

    response = (
        client.table("notifications")
        .select("*")
        .eq("notid", notificationid)
        .execute()
    )

    data = response.data
    if not data:
        return None

    return create_NotificationResponse(data[0])


def add_notification(notification: Notification, client: Optional[Client] = None) -> Optional[NotificationResponse]:
    """
    Add a new notification to the database.
    
    Output:
        A NotificationResponse object for the newly created notification, or None if the notification could not be created.
    """
    if client is None:
        client = get_client()

    response = client.table("notifications").insert(notification.to_dict()).execute()

    if not response.data:
        return None

    return create_NotificationResponse(response.data[0])


def create_notification(notification: NotificationCreateRequest, client: Optional[Client] = None) -> Optional[NotificationResponse]:
    """
    Create a new notification in the database from a NotificationCreateRequest object.
    
    Output:
        A NotificationResponse object for the newly created notification, or None if the notification could not be created.
    """
    if client is None:
        client = get_client()

    notification_obj = Notification(
        userid=notification.userid,
        type=notification.type,
        title=notification.title,
        message=notification.message,
        reference_id=notification.reference_id,
        time=notification.time,
        is_read=notification.is_read,
    )

    return add_notification(notification_obj, client)


def mark_notification_read(notificationid: int, client: Optional[Client] = None) -> Optional[NotificationResponse]:
    """
    Mark a notification as read.
    
    Output:
        A NotificationResponse object for the updated notification, or None if the notification could not be updated.
    """
    if client is None:
        client = get_client()

    response = (
        client.table("notifications")
        .update({"is_read": True})
        .eq("notid", notificationid)
        .execute()
    )

    data = response.data
    if not data:
        return None

    return create_NotificationResponse(data[0])


def remove_notification(notificationid: int, client: Optional[Client] = None) -> bool:
    """
    Remove a notification from the database.
    
    Output:
        True if the notification was removed, False otherwise.
    """
    if client is None:
        client = get_client()

    response = (
        client.table("notifications")
        .delete()
        .eq("notid", notificationid)
        .execute()
    )

    return bool(response.data)


def notification_exists(
    userid: int,
    reference_id: int,
    notification_type: str,
    client: Optional[Client] = None,
) -> bool:
    """
    Check if a notification exists for a user with a given reference_id and type.
    
    Output:
        True if the notification exists, False otherwise.
    """
    if client is None:
        client = get_client()

    response = (
        client.table("notifications")
        .select("notid")
        .eq("userid", userid)
        .eq("reference_id", reference_id)
        .eq("type", notification_type)
        .limit(1)
        .execute()
    )

    return bool(response.data)
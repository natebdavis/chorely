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
    if client is None:
        client = get_client()

    response = client.table("notifications").insert(notification.to_dict()).execute()

    if not response.data:
        return None

    return create_NotificationResponse(response.data[0])


def create_notification(notification: NotificationCreateRequest, client: Optional[Client] = None) -> Optional[NotificationResponse]:
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
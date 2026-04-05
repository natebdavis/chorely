from app.db.client import get_client

from app.db.auth_repo import (
    authenticate_user,
    get_current_user,
)

from app.db.user_repo import (
    add_user,
    get_user,
    get_users,
    is_email_available,
    is_phone_num_available,
    is_username_available,
    remove_user,
)

from app.db.chore_repo import (
    add_chore,
    get_all_completed_chores,
    get_all_in_progress_assigned_chores,
    get_all_requested_chores,
    get_chore,
    get_chores,
    remove_chore,
    update_chore,
)

from app.db.household_repo import (
    create_household_db,
    delete_household_if_empty,
    get_household_member_count,
    get_householdid,
    household_exists,
    join_household,
    leave_household,
)

from app.db.notification_repo import (
    add_notification,
    create_notification,
    get_notification,
    get_notifications,
    mark_notification_read,
    remove_notification,
)

from app.db.invite_repo import (
    cancel_pending_invites_for_user,
    create_invite,
    get_invite,
    get_outgoing_pending_invites,
    get_user_invites,
    get_user_pending_invites,
    get_pending_invite_for_household_user,
    update_invite_status,
)

__all__ = [
    "get_client",
    "authenticate_user",
    "get_current_user",
    "add_user",
    "get_user",
    "get_users",
    "is_email_available",
    "is_phone_num_available",
    "is_username_available",
    "remove_user",
    "add_chore",
    "get_all_completed_chores",
    "get_all_in_progress_assigned_chores",
    "get_all_requested_chores",
    "get_chore",
    "get_chores",
    "remove_chore",
    "update_chore",
    "create_household_db",
    "delete_household_if_empty",
    "get_household_member_count",
    "get_householdid",
    "household_exists",
    "join_household",
    "leave_household",
    "add_notification",
    "create_notification",
    "get_notification",
    "get_notifications",
    "mark_notification_read",
    "remove_notification",
    "cancel_pending_invites_for_user",
    "create_invite",
    "get_invite",
    "get_outgoing_pending_invites",
    "get_user_invites",
    "get_user_pending_invites",
    "get_pending_invite_for_household_user",
    "update_invite_status",
]
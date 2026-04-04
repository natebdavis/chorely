"""
Compatibility layer for database-related imports.

This module re-exports repository functions from app.db so that
existing imports like `from app.database import ...` continue to work
while the codebase is being refactored.

Contributors: Edmund Krajewski, Gilligan Berlinski, Nathaniel Davis
"""

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
    get_notification,
    get_notifications,
    remove_notification,
)

__all__ = [
    "get_client",

    # auth
    "authenticate_user",
    "get_current_user",

    # users
    "add_user",
    "get_user",
    "get_users",
    "is_email_available",
    "is_phone_num_available",
    "is_username_available",
    "remove_user",

    # chores
    "add_chore",
    "get_all_completed_chores",
    "get_all_in_progress_assigned_chores",
    "get_all_requested_chores",
    "get_chore",
    "get_chores",
    "remove_chore",
    "update_chore",

    # households
    "create_household_db",
    "delete_household_if_empty",
    "get_household_member_count",
    "get_householdid",
    "household_exists",
    "join_household",
    "leave_household",

    # notifications
    "add_notification",
    "get_notification",
    "get_notifications",
    "remove_notification",
]
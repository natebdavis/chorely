from app.db.client import get_client

from app.db.auth_repo import (
    authenticate_user,
    get_current_user,
)

from app.db.user_repo import (
    add_user,
    get_user,
    get_users,
    get_all_users,
    is_email_available,
    is_phone_num_available,
    is_username_available,
    remove_user,
    get_requester,
    update_user_password,
    upload_profile_pic,
    get_profile_pic_url,
    delete_profile_pic,
)

from app.db.chore_repo import (
    add_chore,
    get_all_completed_chores,
    get_all_in_progress_assigned_chores,
    get_all_requested_chores,
    get_assigned_chores_in_range,
    get_chore,
    get_chores,
    get_chores_in_range,
    remove_chore,
    update_chore,
    edit_chore,
    get_filtered_chores,
)

from app.db.chore_template_repo import (
    add_chore_template,
    get_chore_template,
    get_chore_templates,
    update_chore_template,
    deactivate_chore_template,
)

from app.db.household_repo import (
    create_household_db,
    delete_household_if_empty,
    get_household_member_count,
    get_householdid,
    household_exists,
    join_household,
    leave_household,
    get_owner_householdid,
    transfer_household_ownership,
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

from app.db.request_repo import (
    get_request,
    update_request,
    get_outgoing_pending_requests,
    get_user_requests,
    create_request,
)

from app.db.leaderboard_repo import (
    get_leaderboard
)

__all__ = [
    "get_client",
    "authenticate_user",
    "get_current_user",

    # users
    "add_user",
    "get_user",
    "get_users",
    "get_all_users",
    "is_email_available",
    "is_phone_num_available",
    "is_username_available",
    "remove_user",
    "get_requester",
    "update_user_password",
    "upload_profile_pic",
    "get_profile_pic_url",
    "delete_profile_pic",

    # chores
    "add_chore",
    "get_all_completed_chores",
    "get_all_in_progress_assigned_chores",
    "get_all_requested_chores",
    "get_assigned_chores_in_range",
    "get_chore",
    "get_chores",
    "get_chores_in_range",
    "remove_chore",
    "update_chore",
    "edit_chore",
    "get_filtered_chores",

    # recurring chore templates
    "add_chore_template",
    "get_chore_template",
    "get_chore_templates",
    "update_chore_template",
    "deactivate_chore_template",

    # households
    "create_household_db",
    "delete_household_if_empty",
    "get_household_member_count",
    "get_householdid",
    "household_exists",
    "join_household",
    "leave_household",
    "get_owner_householdid",
    "transfer_household_ownership",

    # notifications
    "add_notification",
    "create_notification",
    "get_notification",
    "get_notifications",
    "mark_notification_read",
    "remove_notification",

    # invites
    "cancel_pending_invites_for_user",
    "create_invite",
    "get_invite",
    "get_outgoing_pending_invites",
    "get_user_invites",
    "get_user_pending_invites",
    "get_pending_invite_for_household_user",
    "update_invite_status",

    # requests
    "get_request",
    "update_request",
    "get_outgoing_pending_requests",
    "get_user_requests",
    "create_request",

    # leaderboard
    "get_leaderboard"
]
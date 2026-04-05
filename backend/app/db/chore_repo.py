from collections.abc import Iterable
from typing import Union

from supabase import Client

from app.chore import (
    CHORE_TABLE_NAME,
    Chore_Col_Name,
    ChoreCreateRequest,
    ChoreResponse,
    Status,
    create_ChoreResponse,
)
from app.db.client import get_client
from app.user import UserResponse, search_user
from app.db.user_repo import get_user, get_users

"""
Module for chore-related database operations.

Contributors: Edmund Krajewski, Gilligan Berlinski, Nathaniel Davis
"""

first = 0

def get_chore(
    choreid: int,
    client: Union[Client, None] = None,
) -> Union[ChoreResponse, None]:
    """
    Get a single chore given a choreid.

    Output:
        A ChoreResponse matching the choreid, or None if not found.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(CHORE_TABLE_NAME)
        .select("*")
        .eq(Chore_Col_Name.choreid.value, choreid)
        .execute()
    )

    data = response.data
    if not data:
        return None

    chore_row = data[first]
    assignee_id = chore_row[Chore_Col_Name.assignee.value]
    assignee = get_user(userid=assignee_id, client=client) if assignee_id else None

    return create_ChoreResponse(data=chore_row, assignee=assignee)


def get_chores(
    householdid: int,
    client: Union[Client, None] = None,
) -> Union[Iterable[ChoreResponse], None]:
    """
    Get all chores in a household.

    Output:
        An iterable of ChoreResponse objects in the specified household,
        or None if no chores are found.

    Raises:
        ValueError if a chore is assigned to a user not in that household.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(CHORE_TABLE_NAME)
        .select("*")
        .eq(Chore_Col_Name.householdid.value, householdid)
        .execute()
    )

    chore_data = response.data
    if not chore_data:
        return None

    users = get_users(householdid=householdid, client=client)
    users = list(users) if users else []

    chores = []

    for chore in chore_data:
        assignee_id = chore[Chore_Col_Name.assignee.value]

        if assignee_id is None:
            chores.append(create_ChoreResponse(data=chore, assignee=None))
            continue

        assignee: Union[UserResponse, None] = search_user(assignee_id, users)

        if assignee is None:
            error_choreid = chore[Chore_Col_Name.choreid.value]
            raise ValueError(
                f"Chore id: {error_choreid} has an assignee not apart of the household."
            )

        chores.append(create_ChoreResponse(data=chore, assignee=assignee))

    return chores


def add_chore(
    chore: ChoreCreateRequest,
    client: Union[Client, None] = None,
) -> Union[ChoreResponse, None]:
    """
    Add a chore to the database.

    Output:
        Inserted chore data returned as ChoreResponse, or None if insert failed.
    """
    if client is None:
        client = get_client()

    data = {
        Chore_Col_Name.householdid.value: chore.householdid,
        Chore_Col_Name.cname.value: chore.name,
        Chore_Col_Name.description.value: chore.description,
        Chore_Col_Name.request_date.value: chore.request_date,
        Chore_Col_Name.due_date.value: chore.due_date,
        Chore_Col_Name.requester.value: chore.requester_id,
        Chore_Col_Name.assignee.value: chore.assignee_id,
        Chore_Col_Name.status.value: chore.status,
    }

    response = client.table(CHORE_TABLE_NAME).insert(data).execute()
    rows = response.data

    if not rows:
        return None

    assignee_id = rows[first][Chore_Col_Name.assignee.value]
    assignee = get_user(userid=assignee_id, client=client) if assignee_id else None

    return create_ChoreResponse(rows[first], assignee=assignee)


def remove_chore(
    householdid: int,
    choreid: int,
    client: Union[Client, None] = None,
) -> bool:
    """
    Remove a chore from the database.

    Output:
        True if the chore was deleted, False otherwise.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(CHORE_TABLE_NAME)
        .delete()
        .eq(Chore_Col_Name.householdid.value, householdid)
        .eq(Chore_Col_Name.choreid.value, choreid)
        .execute()
    )

    return bool(response.data)


def update_chore(
    householdid: int,
    choreid: int,
    status: Union[str, None] = None,
    assignee_id: Union[int, None] = None,
    client: Union[Client, None] = None,
) -> Union[ChoreResponse, None]:
    """
    Update chore data in the database.

    Output:
        Updated chore returned as ChoreResponse, or None if update failed.
    """
    if client is None:
        client = get_client()

    data = {}

    if status is not None:
        data[Chore_Col_Name.status.value] = status

    data[Chore_Col_Name.assignee.value] = assignee_id

    response = (
        client
        .table(CHORE_TABLE_NAME)
        .update(data)
        .eq(Chore_Col_Name.householdid.value, householdid)
        .eq(Chore_Col_Name.choreid.value, choreid)
        .execute()
    )

    rows = response.data
    if not rows:
        return None

    assignee = get_user(userid=assignee_id, client=client) if assignee_id else None
    return create_ChoreResponse(rows[first], assignee=assignee)


def get_all_requested_chores(
    userid: int,
    client: Union[Client, None] = None,
) -> Union[Iterable[ChoreResponse], None]:
    """
    Given a userid, return all chores requested by that user.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(CHORE_TABLE_NAME)
        .select("*")
        .eq(Chore_Col_Name.requester.value, userid)
        .execute()
    )

    data = response.data
    if not data:
        return None

    chores = []
    for row in data:
        assignee_id = row[Chore_Col_Name.assignee.value]
        assignee = get_user(userid=assignee_id, client=client) if assignee_id else None
        chores.append(create_ChoreResponse(row, assignee=assignee))

    return chores


def get_all_in_progress_assigned_chores(
    userid: int,
    client: Union[Client, None] = None,
) -> Union[Iterable[ChoreResponse], None]:
    """
    Given a userid, return all chores assigned to the user and in progress.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(CHORE_TABLE_NAME)
        .select("*")
        .eq(Chore_Col_Name.assignee.value, userid)
        .eq(Chore_Col_Name.status.value, Status.IN_PROGRESS.name)
        .execute()
    )

    data = response.data
    if not data:
        return None

    assignee = get_user(userid=userid, client=client)
    return [create_ChoreResponse(row, assignee=assignee) for row in data]


def get_all_completed_chores(
    userid: int,
    client: Union[Client, None] = None,
) -> Union[Iterable[ChoreResponse], None]:
    """
    Given a userid, return all chores assigned to the user and completed.
    """
    if client is None:
        client = get_client()

    response = (
        client
        .table(CHORE_TABLE_NAME)
        .select("*")
        .eq(Chore_Col_Name.assignee.value, userid)
        .eq(Chore_Col_Name.status.value, Status.COMPLETE.name)
        .execute()
    )

    data = response.data
    if not data:
        return None

    assignee = get_user(userid=userid, client=client)
    return [create_ChoreResponse(row, assignee=assignee) for row in data]
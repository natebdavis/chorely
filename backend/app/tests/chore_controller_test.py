import datetime as DT

from fastapi.security import OAuth2PasswordRequestForm

from app.controllers.chore_controller import *
from app.controllers.auth_controller import login_for_access_token
from app.database import add_user, remove_user
from app.user import User, UserCreateRequest
from app.chore import Status
from app.controllers.user_controller import create_user

"""
Module for testing the Chore controller module.
Uses pytest (https://docs.pytest.org/en/latest/)
To run, use "python -m pytest" instead of "pytest", as tests are in a subfolder.

Contributors: Nathaniel Davis
"""


def test_create_get_remove_chore():
    
    """Tests if test_create_chore works.
    Assumes that database.remove_chore() and database.get_chore() work."""

    name = "bobs chore",
    description = "this is bobs chore",
    due_date = "2026-04-03T21:52:00+00:00",
    assignee_id = 1

    request = ChoreCreateRequest(
        name = "bobs chore",
        description = "this is bobs chore",
        due_date = "2026-04-03T21:52:00+00:00",
        assignee_id = assignee_id
    )
    chore = Chore(
        name = name,
        description = description,
        due_date = DT.datetime.fromisoformat("2026-04-03T21:52:00+00:00"),
        requester = database.get_user(assignee_id),
        choreid = -1,
        assignee = database.get_user(assignee_id),
        request_date = DT.datetime.fromisoformat("2026-04-03T21:52:00+00:00"),
        status = Status.IN_PROGRESS,
        householdid = 1
    )
    username="bob123"
    password="123"
    fname="bob"
    lname="bobbington"
    email="bob@gmail.com"

    user_create_request = UserCreateRequest(
        username=username,
        password=password,
        fname=fname,
        lname=lname,
        email=email
    )
    user = User(
        username=username,
        passhash="",
        userid=99,
        fname=fname,
        lname=lname,
        email=email
    )
    
    # make temp user
    create_user_response = create_user(user_create_request)

    # get token
    oauth_request = OAuth2PasswordRequestForm(username=username, password=password)
    token = login_for_access_token(oauth_request)

    # make temp chore
    create_chore_response = create_chore(request)

    # test if chore was made
    choreid: int = create_chore_response.choreid
    chore2 = get_chore(choreid)
    assert chore2

    # test if chore was removed
    delete_request = ChoreDeleteRequest(
        choreid = choreid
    )
    delete_chore(delete_request)
    chore2 = get_chore(choreid)
    assert not chore2

    # remove temp user
    user.userid = create_user_response["userid"]
    remove_user(user)
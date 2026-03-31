from app.controllers.user_controller import *
from app.database import get_user, remove_user

"""
Module for testing the User controller module.
Uses pytest (https://docs.pytest.org/en/latest/)
To run, use "python -m pytest" instead of "pytest", as tests are in a subfolder.

Contributors: Nathaniel Davis
"""


def test_create_user():
    
    """Tests if test_create_user works.
    Assumes that database.remove_user() and database.get_user() work."""

    username="bob123"
    fname="bob"
    lname="bobbington"
    email="bob@gmail.com"

    request = UserCreateRequest(
        username=username,
        password="123",
        fname=fname,
        lname=lname,
        email=email
    )
    user = User(
        username=username,
        passhash="",
        userid=-1,
        fname=fname,
        lname=lname,
        email=email
    )

    # make temp user
    response = create_user(request)

    # test if user was made
    userid: int = response["userid"]
    user2 = get_user(userid)
    assert user2
    user.userid = user2.userid
    assert user2 == user

    # test if user was removed
    remove_user(user2)
    user2 = get_user(userid)
    assert not user2
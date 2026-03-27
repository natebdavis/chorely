from app.database import *

"""
Module for testing the User module.
Uses pytest (https://docs.pytest.org/en/latest/)

Contributors: Nathaniel Davis
"""


def test_add_user():
    userid = 123
    user: User = User(
        username="bob123",
        passhash="temp",
        userid=userid,
        fname="bob",
        lname="bobbington",
        email="bob@gmail.com"
        # householdid=456 # need to implement adding households
    )
    add_user(user)

    assert get_user(userid) == user
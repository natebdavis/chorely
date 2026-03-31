from app.database import *

"""
Module for testing the User module.
Uses pytest (https://docs.pytest.org/en/latest/)
To run, use "python -m pytest" instead of "pytest", as tests are in a subfolder.

Contributors: Nathaniel Davis
"""


def test_add_get_remove_user():
    
    """Tests if add_user, get_user, and remove_user work. Ideally, these would be separate test functions, but 
    they are needed for each others' tests."""

    user = User(
        username="bob123",
        passhash="",
        userid=-1,
        fname="bob",
        lname="bobbington",
        email="bob@gmail.com"
        # householdid=456 # need to implement adding households
    )
    
    # make temp user
    response = add_user(user)

    # test if user was made
    userid: int = response[0]["userid"]
    user2 = get_user(userid)
    assert user2
    user.userid = user2.userid
    assert user2 == user

    # test if user was removed
    remove_user(user2)
    user2 = get_user(userid)
    assert not user2
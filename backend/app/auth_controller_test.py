from app.controllers.auth_controller import *
from app.controllers.user_controller import create_user
from app.database import remove_user
from app.user import User, UserCreateRequest

"""
Module for testing the auth controller module.
Uses pytest (https://docs.pytest.org/en/latest/)

Contributors: Nathaniel Davis
"""


def test_login_readme():
    
    """Tests if login_for_access_token and read_me work.
    Assumes that database.add_user() and database.remove_user() work."""

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
        userid=39,
        fname=fname,
        lname=lname,
        email=email
    )
    
    # make temp user
    response = create_user(user_create_request)

    # get token
    oauth_request = OAuth2PasswordRequestForm(username=username, password=password)
    token = login_for_access_token(oauth_request)
    assert token and token["access_token"]

    # check if read_me allows access
    user_response = UserResponse(username=username, fname=fname, lname=lname, email=email, phone_num=None)
    read_me_response = read_me(user_response)
    assert read_me_response

    # clean up temp user
    user.userid = response["userid"]
    remove_user(user)
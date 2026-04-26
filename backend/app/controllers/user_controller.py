"""
Module for managing User Controller operations.
Handles HTTP requests related to Users and exposes API endpoints
for creating and retrieving Users in the system.

Contributors: Edmund Krajewski, Gilligan Berlinski
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import List
import uuid, mimetypes

from app.database import (
    get_user,
    get_users,
    get_all_users,
    add_user,
    is_username_available,
    is_email_available,
    is_phone_num_available,
    get_current_user,
    update_user_password,
    upload_profile_pic,
    get_profile_pic_url,
    delete_profile_pic,
)
from app.user import UserProfilePicResponse, UserResponse, UserCreateRequest, UserPasswordUpdateRequest
from app.utils import get_password_hash, ALLOWED_IMAGE_TYPES, ALLOWED_EXTENSIONS, MAX_FILE_SIZE

router = APIRouter(tags=["users"], prefix="/user")
""" API router for user-related endpoints."""



@router.get("/search", response_model=list[UserResponse])
def search_users(
    q: str,
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Search users by username
    """
    if len(q.strip()) < 2:
        return []

    users = get_all_users()
    query = q.lower().strip()

    results = []

    for user in users:
        if user.userid == current_user.userid:
            continue

        if user.householdid == current_user.householdid:
            continue

        if user.householdid is not None:
           continue

        if (
            query in user.username.lower()
        ):
            results.append(user)
            
    return results


@router.get("/by-username/{username}", response_model=UserResponse)
def get_user_by_username_route(username: str):
    """
    Retrieve a single user by username.

    Raises:
    - HTTPException 404: If the user is not found.
    """
    user = get_user(username=username)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user

@router.get("/profile-pic", response_model=UserProfilePicResponse)
def fetch_profile_pic(current_user: UserResponse = Depends(get_current_user)):
    """
    Retrieve the public profile picture URL of the currently authenticated user.

    Raises:
    - HTTPException 404: If the user does not have a profile picture.
    """
    profile_pic_url = get_profile_pic_url(userid=current_user.userid)

    if not profile_pic_url:
        raise HTTPException(status_code=404, detail="Profile picture not found")

    return profile_pic_url

@router.get("/{userid}", response_model=UserResponse)
def get_single_user(userid: int):
    """
    Retrieve a single user by userid.

    Raises:
    - HTTPException 404: If the user is not found.
    """
    user = get_user(userid=userid)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("", response_model=UserResponse, summary="Get my profile (protected)")
def read_me(current_user: UserResponse = Depends(get_current_user)):
    """
    Retrieve the profile of the currently authenticated user.
    """
    return current_user


@router.post("/create")
def create_user(request: UserCreateRequest):
    """
    Create a new user in the database.

    Raises:
    - HTTPException 409: If the username, email, or phone number is already in use.
    - HTTPException 500: If there is an error creating the user.
    """
    if not is_username_available(request.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username not available")

    if not is_email_available(request.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email not available")

    if request.phone_num is not None and not is_phone_num_available(request.phone_num):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone number not available")

    request.password = get_password_hash(request.password)
    created_user = add_user(request)

    if not created_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")

    return {
        "message": "User created successfully",
        "userid": created_user.userid,
    }

@router.patch("/update-password")
def update_password(request: UserPasswordUpdateRequest, current_user: UserResponse = Depends(get_current_user)):
    """
    Update the password of the currently authenticated user.

    Raises:
    - HTTPException 404: If the user is not found.
    - HTTPException 400: If the current password is incorrect, or if the new password is invalid, or if there is an error updating the password.
    """
    
    try:
        success = update_user_password(request, current_user.userid)
    except TypeError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update password")

    return {"message": "Password updated successfully"}

@router.delete("/delete-profile-pic")
def delete_profile_picture(current_user: UserResponse = Depends(get_current_user)):
    """
    Delete the profile picture of the currently authenticated user.

    Raises:
    - HTTPException 404: If the user does not have a profile picture to delete.
    - HTTPException 400: If there was an error deleting the profile picture.
    - HTTPException 500: If there was an internal server error while attempting to delete the profile picture.
    """

    profile_pic = get_profile_pic_url(userid=current_user.userid)

    if not profile_pic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User does not have a profile picture to delete")

    try:
        success = delete_profile_pic(userid=current_user.userid)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to delete profile picture")

    return {"message": "Profile picture deleted successfully"}

@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
):
    """
    Upload a profile picture for the currently authenticated user. If the user already has a profile picture, the existing picture will be deleted before uploading the new one.
    The uploaded file is validated to ensure it is an allowed image type and does not exceed the maximum file size.
    
    Raises:
    - HTTPException 400: If the uploaded file is not an allowed image type or exceeds the maximum file size.
    - HTTPException 500: If there was an internal server error while attempting to upload the profile picture.
    - HTTPException 404: If the user does not have an existing profile picture to delete.
    - HTTPException 413: If the uploaded file exceeds the maximum allowed size.
    """
    
    existing_url = get_profile_pic_url(userid=current_user.userid)

    if existing_url:
        try:
            delete_profile_pic(userid=current_user.userid)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete existing profile picture: {str(e)}")

    # Validate extension
    file_ext = file.filename.split(".")[-1].lower()

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed (jpg, jpeg, png, webp, gif)",
        )

    # Verify file size
    file_data = await file.read()

    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Max allowed size is 50MB.",
        )  

    # Detect MIME type safely
    content_type, _ = mimetypes.guess_type(file.filename)
    content_type = content_type or "image/jpeg"

    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image type: {content_type}",
        )

    # Generate safe filename
    file_name = f"{uuid.uuid4()}.{file_ext}"

    try:
        success = upload_profile_pic(
            userid=current_user.userid,
            profile_path=file_name,
            profile_data=file_data,
            profile_file_options={
                "content-type": content_type  
            },
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return success
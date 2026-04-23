from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import uuid, mimetypes

from app.database import (
    get_user,
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

"""
Module for managing User Controller operations.
Handles HTTP requests related to Users and exposes API endpoints
for creating and retrieving Users in the system.

Contributors: Edmund Krajewski, Gilligan Berlinski
"""

router = APIRouter(tags=["users"], prefix="/user")


@router.get("/by-username/{username}", response_model=UserResponse)
def get_user_by_username_route(username: str):
    """
    Retrieve a single user by username.
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
    profile_pic_url = get_profile_pic_url(userid=current_user.userid)

    if not profile_pic_url:
        raise HTTPException(status_code=404, detail="Profile picture not found")

    return profile_pic_url

@router.get("/{userid}", response_model=UserResponse)
def get_single_user(userid: int):
    """
    Retrieve a single user by userid.
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
    """
    if not is_username_available(request.username):
        raise HTTPException(status_code=409, detail="Username not available")

    if not is_email_available(request.email):
        raise HTTPException(status_code=409, detail="Email not available")

    if request.phone_num is not None and not is_phone_num_available(request.phone_num):
        raise HTTPException(status_code=409, detail="Phone number not available")

    request.password = get_password_hash(request.password)
    created_user = add_user(request)

    if not created_user:
        raise HTTPException(status_code=500, detail="Failed to create user")

    return {
        "message": "User created successfully",
        "userid": created_user.userid,
    }

@router.patch("/update-password")
def update_password(request: UserPasswordUpdateRequest, current_user: UserResponse = Depends(get_current_user)):
    """
    Update the password of the currently authenticated user.
    """
    
    try:
        success = update_user_password(request, current_user.userid)
    except TypeError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not success:
        raise HTTPException(status_code=400, detail="Failed to update password")

    return {"message": "Password updated successfully"}

@router.delete("/delete-profile-pic")
def delete_profile_picture(current_user: UserResponse = Depends(get_current_user)):
    """
    Delete the profile picture of the currently authenticated user.
    """

    profile_pic = get_profile_pic_url(userid=current_user.userid)

    if not profile_pic:
        raise HTTPException(status_code=404, detail="User does not have a profile picture to delete")

    try:
        success = delete_profile_pic(userid=current_user.userid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete profile picture")

    return {"message": "Profile picture deleted successfully"}

@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
):
    
    existing_url = get_profile_pic_url(userid=current_user.userid)

    if existing_url:
        try:
            delete_profile_pic(userid=current_user.userid)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete existing profile picture: {str(e)}")

    # 🔍 Validate extension
    file_ext = file.filename.split(".")[-1].lower()

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only image files are allowed (jpg, jpeg, png, webp, gif)",
        )

    # 🔍 Read file first (needed for validation)
    file_data = await file.read()

    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File too large. Max allowed size is 50MB.",
        )  

    # 🔍 Detect MIME type safely (DO NOT trust client)
    content_type, _ = mimetypes.guess_type(file.filename)
    content_type = content_type or "image/jpeg"

    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image type: {content_type}",
        )

    # 🔐 Generate safe filename
    file_name = f"{uuid.uuid4()}.{file_ext}"

    # 📤 Upload to Supabase
    try:
        success = upload_profile_pic(
            userid=current_user.userid,
            profile_path=file_name,
            profile_data=file_data,
            profile_file_options={
                "content-type": content_type  # ✅ CRITICAL FIX
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return success
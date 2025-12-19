import os
import shutil
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.schemas.response import StandardResponse

router = APIRouter()


@router.get("/me", response_model=StandardResponse[schemas.user.User])
def read_user_me(
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Get current user profile.**

    Retrieves the authenticated user's details including name, email, and profile image path.
    
    Returns the user object.
    """
    if not current_user.profile_image:
        current_user.profile_image = "static/default_headshot.png"
    return {
        "message": "Profile retrieved successfully",
        "data": current_user
    }


@router.put("/me", response_model=StandardResponse[schemas.user.User])
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.user.UserUpdate,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Update current user profile.**

    Update current user's full name, email, or password.
    
    - If updating **password**, `confirm_password` must be provided and match.
    
    Returns the updated user object.
    """
    if user_in.password:
        if user_in.password != user_in.confirm_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Passwords do not match"
            )
    
    updated_user = crud.crud_user.user.update(db, db_obj=current_user, obj_in=user_in)
    return {
        "message": "Profile updated successfully",
        "data": updated_user
    }


@router.post("/me/reset-password", response_model=StandardResponse[None])
def reset_password_me(
    *,
    db: Session = Depends(deps.get_db),
    reset_in: schemas.user.UserResetPassword,
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Reset password for current user.**

    Dedicated endpoint for password changes.
    
    - **old_password**: Current password for verification.
    - **new_password**: The new password to set.
    - **confirm_new_password**: Must match `new_password`.
    """
    if not crud.crud_user.user.authenticate(db, email=current_user.email, password=reset_in.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid current password"
        )
    
    if reset_in.new_password != reset_in.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="New passwords do not match"
        )
    
    crud.crud_user.user.update(db, db_obj=current_user, obj_in={"password": reset_in.new_password})
    return {
        "message": "Password changed successfully",
        "data": None
    }


@router.post("/me/profile-image", response_model=StandardResponse[schemas.user.User])
async def update_profile_image(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
    current_user: models.user.User = Depends(deps.get_current_user),
) -> Any:
    """
    **Update profile picture.**

    Upload an image file to set as the profile picture.
    
    - **file**: Image file (multipart/form-data).
    
    Returns the user object with the updated `profile_image` path.
    """
    upload_dir = "static/uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file_extension = os.path.splitext(file.filename)[1]
    file_name = f"profile_{current_user.id}{file_extension}"
    file_path = os.path.join(upload_dir, file_name)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update DB with forward slashes for URL consistency
    db_path = file_path.replace("\\", "/")
    updated_user = crud.crud_user.user.update(db, db_obj=current_user, obj_in={"profile_image": db_path})
    
    return {
        "message": "Profile image updated successfully",
        "data": updated_user
    }

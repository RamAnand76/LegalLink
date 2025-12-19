from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas.response import StandardResponse

router = APIRouter()


@router.post("/signup", response_model=StandardResponse[schemas.user.User], status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.user.UserCreate,
) -> Any:
    """
    **Register a new user.**

    This endpoint creates a new user account in the system.
    
    - **full_name**: User's full name.
    - **email**: A unique, valid email address.
    - **password**: A strong password.
    - **confirm_password**: Must match the password.
    
    Returns the created user object if successful.
    """
    if user_in.password != user_in.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match.",
        )
    user = crud.crud_user.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )
    new_user = crud.crud_user.user.create(db, obj_in=user_in)
    return {
        "message": "User registered successfully",
        "data": new_user
    }


@router.post("/login", response_model=StandardResponse[schemas.token.Token])
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    **Login to get an access token.**

    OAuth2 compatible token login. Use the returned `access_token` in the `Authorization` header as a `Bearer` token for protected requests.
    
    - **username**: The user's email address.
    - **password**: The user's password.
    
    Returns a JWT access token if credentials are valid.
    """
    user = crud.crud_user.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Incorrect email or password"
        )
    elif not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="User account is inactive"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
    return {
        "message": "Login successful",
        "data": token
    }

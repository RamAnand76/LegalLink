from typing import Optional
from pydantic import BaseModel, EmailStr


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str
    confirm_password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None
    confirm_password: Optional[str] = None


# Properties to receive via API for password reset
class UserResetPassword(BaseModel):
    old_password: str
    new_password: str
    confirm_new_password: str


# Additional properties to return via API
class User(UserBase):
    id: int
    is_active: bool
    profile_image: Optional[str] = None

    class Config:
        from_attributes = True

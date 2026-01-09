from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = Field(None, example="john.doe@example.com")
    full_name: Optional[str] = Field(None, example="John Doe")


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr = Field(..., example="john.doe@example.com")
    password: str = Field(..., min_length=6, example="SecurePass@123")
    confirm_password: str = Field(..., example="SecurePass@123")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "password": "SecurePass@123",
                "confirm_password": "SecurePass@123"
            }
        }
    )


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=6, example="NewSecurePass@456")
    confirm_password: Optional[str] = Field(None, example="NewSecurePass@456")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "john.smith@example.com",
                "full_name": "John Smith"
            }
        }
    )


# Properties to receive via API for password reset
class UserResetPassword(BaseModel):
    old_password: str = Field(..., example="OldSecurePass@123")
    new_password: str = Field(..., min_length=6, example="NewSecurePass@456")
    confirm_new_password: str = Field(..., example="NewSecurePass@456")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "old_password": "OldSecurePass@123",
                "new_password": "NewSecurePass@456",
                "confirm_new_password": "NewSecurePass@456"
            }
        }
    )


# Additional properties to return via API
class User(UserBase):
    id: int = Field(..., example=1)
    is_active: bool = Field(..., example=True)
    profile_image: Optional[str] = Field(None, example="static/uploads/profile_1.jpg")

    model_config = ConfigDict(from_attributes=True)

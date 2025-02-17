from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict

class UserBase(BaseModel):
    """Base schema with common user attributes"""
    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(..., min_length=2, description="User's full name")
    is_active: bool = Field(default=True, description="Whether the user is active")

class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(
        ...,
        min_length=8,
        description="User's password (min 8 characters)"
    )

class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = Field(None, description="User's email address")
    name: Optional[str] = Field(None, min_length=2, description="User's full name")
    password: Optional[str] = Field(
        None,
        min_length=8,
        description="User's password (min 8 characters)"
    )
    is_active: Optional[bool] = Field(None, description="Whether the user is active")

    model_config = ConfigDict(exclude_unset=True)

class UserInDB(UserBase):
    """Schema for user as stored in database"""
    id: int = Field(..., description="User's unique identifier")
    hashed_password: str = Field(..., description="Hashed password")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserBase):
    """Schema for user data returned to clients"""
    id: int = Field(..., description="User's unique identifier")
    created_at: datetime = Field(..., description="When the user was created")

    model_config = ConfigDict(from_attributes=True)

class UserAuth(BaseModel):
    """Schema for user authentication"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

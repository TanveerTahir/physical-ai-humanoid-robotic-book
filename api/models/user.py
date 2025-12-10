from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID, uuid4


class User(BaseModel):
    """
    User model for the Physical AI & Humanoid Robotics textbook platform.
    Represents platform users with authentication and personalization data.
    """
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    name: str = Field(min_length=2, max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    preferences: Optional[dict] = Field(default={})
    learning_path: Optional[dict] = Field(default={})
    personalization_profile: Optional[dict] = Field(default={})

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }


class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    """
    email: EmailStr
    name: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    """
    Schema for updating user information.
    """
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    preferences: Optional[dict] = None
    learning_path: Optional[dict] = None
    personalization_profile: Optional[dict] = None


class UserInDB(User):
    """
    User model that includes hashed password for database storage.
    """
    hashed_password: str
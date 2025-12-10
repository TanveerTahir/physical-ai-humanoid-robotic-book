from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from enum import Enum


class InteractionType(str, Enum):
    """Enumeration of interaction types"""
    QUERY = "query"
    TRANSLATION = "translation"
    PERSONALIZATION = "personalization"
    RAG = "rag"
    AUTH = "auth"


class UserInteraction(BaseModel):
    """
    UserInteraction model for the Physical AI & Humanoid Robotics textbook platform.
    Represents user interactions with AI features and content.
    """
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    chapter_id: Optional[UUID] = None  # Optional since some interactions may be global
    interaction_type: InteractionType
    input: str
    output: str
    context: Optional[dict] = Field(default={})
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str,
            InteractionType: lambda v: v.value
        }


class UserInteractionCreate(BaseModel):
    """
    Schema for creating a new user interaction.
    """
    user_id: UUID
    chapter_id: Optional[UUID] = None
    interaction_type: InteractionType
    input: str
    output: str
    context: Optional[dict] = Field(default={})
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)


class UserInteractionUpdate(BaseModel):
    """
    Schema for updating user interaction information.
    """
    output: Optional[str] = None
    context: Optional[dict] = None
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5)
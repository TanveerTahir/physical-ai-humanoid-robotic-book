from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class TranslationCache(BaseModel):
    """
    TranslationCache model for the Physical AI & Humanoid Robotics textbook platform.
    Represents caching layer for Urdu translations.
    """
    id: UUID = Field(default_factory=uuid4)
    original_text: str
    urdu_translation: str
    chapter_id: Optional[UUID] = None  # Optional since some translations may be reusable
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    usage_count: int = Field(ge=0, default=0)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }


class TranslationCacheCreate(BaseModel):
    """
    Schema for creating a new translation cache entry.
    """
    original_text: str
    urdu_translation: str
    chapter_id: Optional[UUID] = None
    expires_at: Optional[datetime] = None


class TranslationCacheUpdate(BaseModel):
    """
    Schema for updating translation cache information.
    """
    urdu_translation: Optional[str] = None
    expires_at: Optional[datetime] = None
    usage_count: Optional[int] = Field(None, ge=0)
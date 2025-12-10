from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from .chapter import SectionType


class Section(BaseModel):
    """
    Section model for the Physical AI & Humanoid Robotics textbook.
    Represents grouping of related chapters (A-H as defined in spec).
    """
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    section_type: SectionType
    order: int = Field(ge=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str,
            SectionType: lambda v: v.value
        }


class SectionCreate(BaseModel):
    """
    Schema for creating a new section.
    """
    name: str
    description: str
    section_type: SectionType
    order: int = Field(ge=1)


class SectionUpdate(BaseModel):
    """
    Schema for updating section information.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = Field(None, ge=1)
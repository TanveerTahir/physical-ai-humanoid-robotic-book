from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from enum import Enum


class SectionType(str, Enum):
    """Enumeration of textbook sections"""
    FOUNDATIONS = "A"
    ROS_NERVOUS_SYSTEM = "B"
    DIGITAL_TWIN = "C"
    ISAAC_PLATFORM = "D"
    VLA = "E"
    CAPSTONE_PROJECTS = "F"
    ENGINEERING_NOTES = "G"
    APPENDICES = "H"


class Chapter(BaseModel):
    """
    Chapter model for the Physical AI & Humanoid Robotics textbook.
    Represents individual textbook chapters with content and metadata.
    """
    id: UUID = Field(default_factory=uuid4)
    title: str
    slug: str
    section: SectionType
    number: int = Field(ge=1)
    content: str  # Chapter content in MDX format
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    gpu_notes: Optional[str] = None
    jetson_notes: Optional[str] = None
    prerequisites: List[str] = Field(default=[])
    learning_objectives: List[str] = Field(default=[])
    embedded_content: Optional[dict] = Field(default={})

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str,
            SectionType: lambda v: v.value
        }


class ChapterCreate(BaseModel):
    """
    Schema for creating a new chapter.
    """
    title: str
    slug: str
    section: SectionType
    number: int = Field(ge=1)
    content: str
    gpu_notes: Optional[str] = None
    jetson_notes: Optional[str] = None
    prerequisites: List[str] = Field(default=[])
    learning_objectives: List[str] = Field(default=[])
    embedded_content: Optional[dict] = Field(default={})


class ChapterUpdate(BaseModel):
    """
    Schema for updating chapter information.
    """
    title: Optional[str] = None
    content: Optional[str] = None
    gpu_notes: Optional[str] = None
    jetson_notes: Optional[str] = None
    prerequisites: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    embedded_content: Optional[dict] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
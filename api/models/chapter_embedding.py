from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class ChapterEmbedding(BaseModel):
    """
    ChapterEmbedding model for the Physical AI & Humanoid Robotics textbook.
    Represents vector embeddings for RAG system.
    """
    id: UUID = Field(default_factory=uuid4)
    chapter_id: UUID
    content_chunk: str
    embedding_vector: List[float]  # Vector representation of content
    chunk_index: int = Field(ge=0)
    context_window: Optional[str] = None  # Context around the chunk
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }


class ChapterEmbeddingCreate(BaseModel):
    """
    Schema for creating a new chapter embedding.
    """
    chapter_id: UUID
    content_chunk: str
    embedding_vector: List[float]
    chunk_index: int = Field(ge=0)
    context_window: Optional[str] = None


class ChapterEmbeddingUpdate(BaseModel):
    """
    Schema for updating chapter embedding information.
    """
    content_chunk: Optional[str] = None
    embedding_vector: Optional[List[float]] = None
    chunk_index: Optional[int] = Field(None, ge=0)
    context_window: Optional[str] = None
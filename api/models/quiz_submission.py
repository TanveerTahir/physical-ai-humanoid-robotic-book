from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class QuizSubmission(BaseModel):
    """
    QuizSubmission model for the Physical AI & Humanoid Robotics textbook platform.
    Represents user quiz submissions and results.
    """
    id: UUID = Field(default_factory=uuid4)
    quiz_id: UUID
    user_id: UUID
    answers: Dict[str, str]  # Mapping of question_id to user answer
    score: float = Field(ge=0, le=100)  # Score percentage
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    time_taken: int = Field(ge=0)  # Time taken in seconds

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }


class QuizSubmissionCreate(BaseModel):
    """
    Schema for creating a new quiz submission.
    """
    quiz_id: UUID
    user_id: UUID
    answers: Dict[str, str]
    score: float = Field(ge=0, le=100)
    time_taken: int = Field(ge=0)


class QuizSubmissionUpdate(BaseModel):
    """
    Schema for updating quiz submission information.
    """
    answers: Optional[Dict[str, str]] = None
    score: Optional[float] = Field(None, ge=0, le=100)
    completed_at: Optional[datetime] = None
    time_taken: Optional[int] = Field(None, ge=0)
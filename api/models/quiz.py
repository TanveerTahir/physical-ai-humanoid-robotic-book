from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class QuizQuestion(BaseModel):
    """
    Model for a single quiz question.
    """
    id: str
    question_text: str
    question_type: str  # e.g., "multiple_choice", "true_false", "short_answer"
    options: Optional[List[str]] = Field(default=[])  # For multiple choice questions
    correct_answer: str
    explanation: Optional[str] = None


class Quiz(BaseModel):
    """
    Quiz model for the Physical AI & Humanoid Robotics textbook platform.
    Represents chapter quizzes for assessment.
    """
    id: UUID = Field(default_factory=uuid4)
    chapter_id: UUID
    title: str
    description: str
    questions: List[QuizQuestion] = Field(default=[])
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str
        }


class QuizCreate(BaseModel):
    """
    Schema for creating a new quiz.
    """
    chapter_id: UUID
    title: str
    description: str
    questions: List[QuizQuestion] = Field(default=[])


class QuizUpdate(BaseModel):
    """
    Schema for updating quiz information.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    questions: Optional[List[QuizQuestion]] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)
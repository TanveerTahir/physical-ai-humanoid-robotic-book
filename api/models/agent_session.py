from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from enum import Enum


class AgentType(str, Enum):
    """Enumeration of agent types"""
    QUIZ_GENERATOR = "quiz_generator"
    PERSONALIZATION = "personalization"
    TRANSLATION = "translation"
    VISION_SLAM_EXPLAINER = "vision_slam_explainer"
    ROS_DEBUGGING = "ros_debugging"


class AgentSession(BaseModel):
    """
    AgentSession model for the Physical AI & Humanoid Robotics textbook platform.
    Represents sessions for Claude Code subagents.
    """
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    agent_type: AgentType
    session_data: Optional[dict] = Field(default={})
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_interaction_at: Optional[datetime] = None
    is_active: bool = True

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str,
            AgentType: lambda v: v.value
        }


class AgentSessionCreate(BaseModel):
    """
    Schema for creating a new agent session.
    """
    user_id: UUID
    agent_type: AgentType
    session_data: Optional[dict] = Field(default={})


class AgentSessionUpdate(BaseModel):
    """
    Schema for updating agent session information.
    """
    session_data: Optional[dict] = None
    last_interaction_at: Optional[datetime] = None
    is_active: Optional[bool] = None
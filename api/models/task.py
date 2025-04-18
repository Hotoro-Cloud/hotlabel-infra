from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid

class SessionInfo(BaseModel):
    """Session information for task submission."""
    browser: str
    browser_version: str
    os: str
    screen_resolution: str
    language: str
    timezone: Optional[str] = None
    device_type: Optional[str] = None

class TaskContent(BaseModel):
    """Content of a task, varies by task type."""
    image_url: Optional[str] = None
    question: Optional[str] = None
    text: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    context: Optional[str] = None

class Reward(BaseModel):
    """Reward for completing a task."""
    type: str = "content_access"  # content_access, points, etc.
    duration_seconds: Optional[int] = None
    points: Optional[int] = None
    description: Optional[str] = None

class TaskResponse(BaseModel):
    """API response for a single task."""
    task_id: str = Field(..., description="Unique identifier for the task")
    task_type: str = Field(..., description="Type of task (vqa, text_classification, etc.)")
    content: TaskContent
    options: Optional[List[str]] = None
    time_estimate_seconds: int = Field(5, description="Estimated time to complete the task in seconds")
    complexity_level: int = Field(1, description="Task complexity level from 1-5")
    golden_set: bool = Field(False, description="Whether this is a golden set task for quality control")
    expires_at: datetime = Field(..., description="Time at which the task expires")
    
    @validator('task_id')
    def validate_task_id(cls, v):
        """Validate that task_id is a valid UUID."""
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("task_id must be a valid UUID")

class TaskSummary(BaseModel):
    """Summary of a task for batch response."""
    task_id: str
    task_type: str
    content: TaskContent
    options: Optional[List[str]] = None
    complexity_level: int = 1

class TaskBatchResponse(BaseModel):
    """API response for a batch of tasks."""
    batch_id: str
    tasks: List[TaskSummary]
    expires_at: datetime

class TaskSubmissionRequest(BaseModel):
    """API request for submitting a task result."""
    session_id: str
    publisher_id: str
    response: Union[str, List[str], Dict[str, Any]]
    time_spent_ms: int
    session_info: SessionInfo

class TaskSubmissionResponse(BaseModel):
    """API response for a task submission."""
    success: bool = True
    reward: Reward
    quality_score: float = Field(..., ge=0.0, le=1.0)
    next_task_available: bool = True

# Database models would typically be defined separately in an ORM format
# These are just the API models for requests and responses
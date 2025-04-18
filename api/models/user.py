from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Any, Optional
from datetime import datetime

class ClientInfo(BaseModel):
    """Client information for session initialization."""
    browser: str
    browser_version: str
    os: str
    screen_resolution: str
    language: str
    timezone: Optional[str] = None
    referring_url: Optional[str] = None
    device_type: Optional[str] = Field(None, description="desktop, mobile, tablet")

class ConsentSettings(BaseModel):
    """User consent settings."""
    functional: bool = True
    analytics: bool = True

class SessionInitRequest(BaseModel):
    """API request for initializing a user session."""
    publisher_id: str
    client_info: ClientInfo
    consent: ConsentSettings

class UserProfile(BaseModel):
    """User profile information."""
    language: str
    expertise_level: str = "beginner"
    task_preferences: List[str] = []
    max_complexity: int = 2

class SessionConfig(BaseModel):
    """Configuration for a user session."""
    task_interval_seconds: int = 300
    minimum_view_time_seconds: int = 3
    ui_theme: str = "light"

class SessionInitResponse(BaseModel):
    """API response for session initialization."""
    session_id: str
    expires_at: datetime
    profile: UserProfile
    config: SessionConfig

class LanguageProficiency(BaseModel):
    """User's language proficiency levels."""
    __root__: Dict[str, str]  # e.g., {"en": "native", "fr": "fluent"}

class PerformanceMetrics(BaseModel):
    """User performance metrics."""
    accuracy: float
    average_time_ms: int
    task_completions: int

class ProfileUpdateRequest(BaseModel):
    """API request for updating a user profile."""
    publisher_id: str
    expertise_areas: Optional[List[str]] = None
    task_preferences: Optional[List[str]] = None
    language_proficiency: Optional[LanguageProficiency] = None
    performance_metrics: Optional[PerformanceMetrics] = None

class UpdatedProfile(BaseModel):
    """Updated user profile information."""
    expertise_level: str
    preferred_languages: List[str]
    expertise_areas: List[str]
    max_complexity: int

class ProfileUpdateResponse(BaseModel):
    """API response for profile update."""
    success: bool = True
    updated_profile: UpdatedProfile

class RecentActivity(BaseModel):
    """Recent user activity."""
    task_type: str
    timestamp: datetime
    accuracy: float

class UserRewards(BaseModel):
    """User rewards information."""
    content_access_minutes: int
    quality_points: int

class UserStatsResponse(BaseModel):
    """API response for user statistics."""
    tasks_completed: int
    average_accuracy: float
    average_time_ms: int
    expertise_level: str
    contribution_ranking: int
    recent_activity: List[RecentActivity]
    rewards_earned: UserRewards

class TokenData(BaseModel):
    """Data stored in authentication tokens."""
    publisher_id: str
    is_admin: Optional[bool] = False
    permissions: Optional[List[str]] = []
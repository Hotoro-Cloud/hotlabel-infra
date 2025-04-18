from pydantic import BaseModel, Field, EmailStr, HttpUrl, validator
from typing import List, Dict, Any, Optional

class PublisherRegistrationRequest(BaseModel):
    """API request for registering a new publisher."""
    company_name: str
    website_url: HttpUrl
    contact_email: EmailStr
    contact_name: str
    website_categories: List[str]
    estimated_monthly_traffic: int = Field(..., gt=0)
    integration_platform: str
    preferred_task_types: List[str] = []

class PublisherRegistrationResponse(BaseModel):
    """API response for publisher registration."""
    publisher_id: str
    api_key: str
    dashboard_url: HttpUrl
    integration_guide_url: HttpUrl
    sdk_snippet: str

class ImpressionMetrics(BaseModel):
    """Publisher impression metrics."""
    total_impressions: int
    task_displays: int
    task_completions: int
    completion_rate: float

class RevenueMetrics(BaseModel):
    """Publisher revenue metrics."""
    total_revenue: float
    cpm: float
    estimated_traditional_ad_revenue: float
    revenue_uplift_percentage: float

class UserMetrics(BaseModel):
    """Publisher user metrics."""
    unique_users: int
    returning_users: int
    average_tasks_per_user: float

class TimeSeriesEntry(BaseModel):
    """Time series entry for publisher statistics."""
    date: str  # ISO 8601 date format (yyyy-mm-dd)
    impressions: int
    completions: int
    revenue: float

class PublisherStatisticsResponse(BaseModel):
    """API response for publisher statistics."""
    period: Dict[str, str]  # {"start": "2023-01-01T00:00:00Z", "end": "2023-01-07T00:00:00Z"}
    impression_metrics: ImpressionMetrics
    revenue_metrics: RevenueMetrics
    user_metrics: UserMetrics
    time_series: List[TimeSeriesEntry]

class AppearanceConfig(BaseModel):
    """Publisher appearance configuration."""
    theme: str = "light"
    primary_color: str = "#3366FF"
    border_radius: str = "4px"
    font_family: str = "Roboto, Arial, sans-serif"

class BehaviorConfig(BaseModel):
    """Publisher behavior configuration."""
    task_display_frequency: int = 300
    max_tasks_per_session: int = 5
    show_task_after_seconds: int = 30
    display_on_page_types: List[str] = ["article", "video"]

class TaskPreferencesConfig(BaseModel):
    """Publisher task preferences configuration."""
    preferred_task_types: List[str] = ["vqa", "text_classification"]
    max_complexity_level: int = 3
    preferred_languages: List[str] = ["en"]

class RewardsConfig(BaseModel):
    """Publisher rewards configuration."""
    content_access_duration_seconds: int = 3600
    show_completion_feedback: bool = True

class ConfigurationUpdateRequest(BaseModel):
    """API request for updating publisher configuration."""
    appearance: Optional[AppearanceConfig] = None
    behavior: Optional[BehaviorConfig] = None
    task_preferences: Optional[TaskPreferencesConfig] = None
    rewards: Optional[RewardsConfig] = None

class ConfigurationUpdateResponse(BaseModel):
    """API response for configuration update."""
    success: bool
    updated_at: str  # ISO 8601 format
    effective_from: str  # ISO 8601 format
    configuration_version: int

class IntegrationCodeResponse(BaseModel):
    """API response for integration code generation."""
    platform: str
    code_snippets: Dict[str, str]
    installation_steps: List[str]
    documentation_url: HttpUrl

class WebhookConfigRequest(BaseModel):
    """API request for webhook configuration."""
    endpoint_url: HttpUrl
    secret_key: str
    events: List[str]
    active: bool = True

class WebhookConfigResponse(BaseModel):
    """API response for webhook configuration."""
    webhook_id: str
    status: str
    test_event_url: HttpUrl
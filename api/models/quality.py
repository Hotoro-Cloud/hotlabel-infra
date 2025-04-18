from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ValidationResponse(BaseModel):
    """API response for validation of a label."""
    validation_id: str
    quality_score: float = Field(..., ge=0.0, le=1.0)
    validation_method: str
    issues_detected: List[str] = []
    confidence: str = Field(..., regex="^(low|medium|high)$")
    feedback: str = ""

class MetricsPeriod(BaseModel):
    """Period for quality metrics."""
    start: str  # ISO 8601 format
    end: str    # ISO 8601 format

class QualityMetrics(BaseModel):
    """Overall quality metrics."""
    total_labels: int
    average_quality_score: float
    golden_set_accuracy: float
    consensus_rate: float
    suspicious_activity_percentage: float
    average_time_per_task_ms: int

class TaskTypeMetrics(BaseModel):
    """Quality metrics for a specific task type."""
    total_labels: int
    average_quality_score: float

class TimeSeriesMetrics(BaseModel):
    """Quality metrics for a specific time point."""
    date: str  # ISO 8601 date format (yyyy-mm-dd)
    total_labels: int
    average_quality_score: float

class QualityMetricsResponse(BaseModel):
    """API response for quality metrics."""
    period: MetricsPeriod
    metrics: QualityMetrics
    breakdown_by_task_type: Dict[str, TaskTypeMetrics]
    time_series: List[TimeSeriesMetrics]

class QualityReportRequest(BaseModel):
    """API request for reporting quality issues."""
    publisher_id: str
    session_id: str
    task_id: str
    report_type: str = Field(..., description="Type of quality issue (ambiguous_question, etc.)")
    details: str = Field(..., description="Details about the issue")
    reported_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class QualityReportResponse(BaseModel):
    """API response for quality report submission."""
    report_id: str
    status: str = "received"
    estimated_review_time: str
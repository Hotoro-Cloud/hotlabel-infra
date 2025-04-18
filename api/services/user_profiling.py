import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from api.models.user import (
    SessionInitRequest,
    SessionInitResponse,
    UserProfile,
    SessionConfig,
    ProfileUpdateRequest,
    ProfileUpdateResponse,
    UpdatedProfile,
    UserStatsResponse,
    RecentActivity,
    UserRewards,
)

async def initialize_user_session(
    db: AsyncSession,
    redis: Redis,
    session_request: SessionInitRequest,
) -> SessionInitResponse:
    """
    Initialize a new user session and create a temporary profile.
    
    Args:
        db: Database session
        redis: Redis connection
        session_request: Session initialization request
        
    Returns:
        A SessionInitResponse object
    """
    # In a real implementation, we would:
    # 1. Create a new session in the database
    # 2. Initialize a user profile based on the client info
    # 3. Return the session details
    
    # Generate a new session ID
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    expires_at = datetime.now() + timedelta(hours=24)
    
    # Create a user profile based on the client info
    language = session_request.client_info.language.split("-")[0] if "-" in session_request.client_info.language else session_request.client_info.language
    
    # Determine initial task preferences based on device
    task_preferences = ["vqa", "text_classification"]
    if session_request.client_info.device_type == "mobile":
        # Simpler tasks for mobile users
        task_preferences = ["vqa"]
    
    profile = UserProfile(
        language=language,
        expertise_level="beginner",
        task_preferences=task_preferences,
        max_complexity=2,
    )
    
    # Create session configuration
    config = SessionConfig(
        task_interval_seconds=300,  # 5 minutes between tasks
        minimum_view_time_seconds=3,
        ui_theme="light",
    )
    
    # Store the session in Redis
    session_key = f"session:{session_request.publisher_id}:{session_id}"
    await redis.set(session_key, json.dumps({
        "session_id": session_id,
        "publisher_id": session_request.publisher_id,
        "created_at": datetime.now().isoformat(),
        "expires_at": expires_at.isoformat(),
        "client_info": session_request.client_info.dict(),
        "consent": session_request.consent.dict(),
    }), ex=86400)  # 24 hour expiration
    
    # Store the user profile in Redis
    profile_key = f"user:profile:{session_request.publisher_id}:{session_id}"
    await redis.set(profile_key, json.dumps(profile.dict()), ex=86400)  # 24 hour expiration
    
    # Initialize task completion counter
    await redis.set(f"user:tasks_completed:{session_id}", "0", ex=86400)  # 24 hour expiration
    
    return SessionInitResponse(
        session_id=session_id,
        expires_at=expires_at,
        profile=profile,
        config=config,
    )

async def update_user_profile(
    db: AsyncSession,
    redis: Redis,
    session_id: str,
    profile_update: ProfileUpdateRequest,
) -> Optional[ProfileUpdateResponse]:
    """
    Update a user's profile based on their interaction history.
    
    Args:
        db: Database session
        redis: Redis connection
        session_id: Session ID
        profile_update: Profile update request
        
    Returns:
        A ProfileUpdateResponse object or None if the session is not found
    """
    # Get the current user profile from Redis
    profile_key = f"user:profile:{profile_update.publisher_id}:{session_id}"
    profile_json = await redis.get(profile_key)
    
    if not profile_json:
        # Profile not found
        return None
    
    current_profile = json.loads(profile_json)
    
    # Update the profile based on the request and performance metrics
    expertise_level = current_profile.get("expertise_level", "beginner")
    if profile_update.performance_metrics:
        # Upgrade expertise level based on performance
        if (profile_update.performance_metrics.accuracy >= 0.85 and 
            profile_update.performance_metrics.task_completions >= 10):
            expertise_level = "intermediate"
        if (profile_update.performance_metrics.accuracy >= 0.9 and 
            profile_update.performance_metrics.task_completions >= 50):
            expertise_level = "expert"
    
    # Update expertise areas
    expertise_areas = profile_update.expertise_areas or current_profile.get("expertise_areas", [])
    
    # Update preferred languages
    preferred_languages = []
    if profile_update.language_proficiency:
        # Sort languages by proficiency level
        proficiency_levels = {"native": 3, "fluent": 2, "intermediate": 1, "beginner": 0}
        language_proficiency = profile_update.language_proficiency.__root__
        preferred_languages = sorted(
            language_proficiency.keys(),
            key=lambda lang: proficiency_levels.get(language_proficiency[lang], -1),
            reverse=True
        )
    else:
        preferred_languages = [current_profile.get("language", "en")]
    
    # Calculate max complexity based on expertise level
    max_complexity_map = {"beginner": 2, "intermediate": 3, "expert": 5}
    max_complexity = max_complexity_map.get(expertise_level, 2)
    
    # Create the updated profile
    updated_profile = UpdatedProfile(
        expertise_level=expertise_level,
        preferred_languages=preferred_languages,
        expertise_areas=expertise_areas,
        max_complexity=max_complexity,
    )
    
    # Update the profile in Redis
    current_profile.update({
        "expertise_level": expertise_level,
        "expertise_areas": expertise_areas,
        "preferred_languages": preferred_languages,
        "max_complexity": max_complexity,
    })
    await redis.set(profile_key, json.dumps(current_profile), ex=86400)  # 24 hour expiration
    
    return ProfileUpdateResponse(
        success=True,
        updated_profile=updated_profile,
    )

async def get_user_statistics(
    db: AsyncSession,
    redis: Redis,
    session_id: str,
    publisher_id: str,
) -> Optional[UserStatsResponse]:
    """
    Get statistics about a user's contributions and performance.
    
    Args:
        db: Database session
        redis: Redis connection
        session_id: Session ID
        publisher_id: Publisher ID
        
    Returns:
        A UserStatsResponse object or None if the session is not found
    """
    # Get the user profile from Redis
    profile_key = f"user:profile:{publisher_id}:{session_id}"
    profile_json = await redis.get(profile_key)
    
    if not profile_json:
        # Profile not found
        return None
    
    profile = json.loads(profile_json)
    
    # Get the number of tasks completed
    tasks_completed_str = await redis.get(f"user:tasks_completed:{session_id}")
    tasks_completed = int(tasks_completed_str) if tasks_completed_str else 0
    
    # In a real implementation, we would query the database for the user's statistics
    # For demonstration purposes, we'll create mock statistics
    
    # Create mock recent activity
    recent_activity = []
    for i in range(min(tasks_completed, 5)):
        recent_activity.append(RecentActivity(
            task_type="vqa" if i % 2 == 0 else "text_classification",
            timestamp=datetime.now() - timedelta(minutes=i * 5),
            accuracy=0.8 + (i * 0.05) if i < 4 else 0.0,  # Add some variation
        ))
    
    # Calculate average accuracy from recent activity
    average_accuracy = 0.0
    if recent_activity:
        average_accuracy = sum(activity.accuracy for activity in recent_activity) / len(recent_activity)
    
    # Calculate rewards based on task completion and accuracy
    content_access_minutes = tasks_completed * 5  # 5 minutes per task
    quality_points = int(tasks_completed * average_accuracy * 10)  # 10 points per perfect task
    
    return UserStatsResponse(
        tasks_completed=tasks_completed,
        average_accuracy=average_accuracy,
        average_time_ms=3750,  # Mock average time
        expertise_level=profile.get("expertise_level", "beginner"),
        contribution_ranking=756,  # Mock ranking
        recent_activity=recent_activity,
        rewards_earned=UserRewards(
            content_access_minutes=content_access_minutes,
            quality_points=quality_points,
        ),
    )
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from api.models.task import (
    TaskResponse,
    TaskContent,
    TaskBatchResponse,
    TaskSummary,
    TaskSubmissionRequest,
    TaskSubmissionResponse,
    Reward,
)
from api.services.quality_assurance import validate_label_quality

async def get_next_task(
    db: AsyncSession,
    redis: Redis,
    session_id: str,
    publisher_id: str,
    language: Optional[str] = None,
    website_category: Optional[str] = None,
    previous_task_id: Optional[str] = None,
) -> Optional[TaskResponse]:
    """
    Get the next appropriate task for a user based on their profile and context.
    
    Args:
        db: Database session
        redis: Redis connection
        session_id: User session ID
        publisher_id: Publisher ID
        language: User's preferred language
        website_category: Category of the website the user is visiting
        previous_task_id: ID of the previous task if part of a sequence
        
    Returns:
        A TaskResponse object or None if no tasks are available
    """
    # In a real implementation, we would:
    # 1. Check if the user exists and has an active session
    # 2. Retrieve the user's profile from Redis
    # 3. Query the database for suitable tasks based on user profile and context
    # 4. Select the best task for the user
    # 5. Mark the task as assigned to the user
    
    # Get user profile from Redis
    user_profile_key = f"user:profile:{publisher_id}:{session_id}"
    user_profile_json = await redis.get(user_profile_key)
    
    if not user_profile_json:
        # User profile not found, return None
        return None
    
    user_profile = json.loads(user_profile_json)
    user_language = language or user_profile.get("language", "en")
    user_expertise = user_profile.get("expertise_level", "beginner")
    max_complexity = user_profile.get("max_complexity", 2)
    
    # Mock task selection - in a real implementation, we would query the database
    # For demonstration purposes, we'll create a mock task
    
    # Query TII API or database for a suitable task
    # This is where we'd integrate with the TII alignment database
    task_id = str(uuid.uuid4())
    
    # Create a task based on the user's profile
    # In a real implementation, we would select a task from the database
    complexity_level = min(max_complexity, 3)  # Cap complexity at 3
    
    # Determine if this should be a golden set task (for quality control)
    # In a production system, we would use a more sophisticated algorithm
    # based on user history and task distribution
    golden_set = False
    if user_expertise == "beginner" and await redis.get(f"user:tasks_completed:{session_id}") == "0":
        # First task for beginners should be a golden set task
        golden_set = True
    
    # Mark the task as assigned to prevent duplication
    assignment_key = f"task:assigned:{task_id}"
    await redis.set(assignment_key, session_id, ex=300)  # 5 minute expiration
    
    # Create a task response
    task = TaskResponse(
        task_id=task_id,
        task_type="vqa",
        content=TaskContent(
            image_url=f"https://storage.hotlabel.io/samples/image{task_id[-4:]}.jpg",
            question="What color is the car in this image?",
        ),
        options=["Red", "Blue", "Green", "Yellow"],
        time_estimate_seconds=5,
        complexity_level=complexity_level,
        golden_set=golden_set,
        expires_at=datetime.now() + timedelta(minutes=5),
    )
    
    # Store the task details in Redis for later validation
    task_key = f"task:{task_id}"
    await redis.set(task_key, json.dumps({
        "task_id": task_id,
        "task_type": "vqa",
        "golden_set": golden_set,
        "expected_answer": "Blue" if golden_set else None,
        "publisher_id": publisher_id,
        "session_id": session_id,
        "complexity_level": complexity_level,
        "created_at": datetime.now().isoformat(),
    }), ex=3600)  # 1 hour expiration
    
    return task

async def submit_task_result(
    db: AsyncSession,
    redis: Redis,
    task_id: str,
    submission: TaskSubmissionRequest,
) -> TaskSubmissionResponse:
    """
    Submit a user's response to a labeling task.
    
    Args:
        db: Database session
        redis: Redis connection
        task_id: Task ID
        submission: Task submission request
        
    Returns:
        A TaskSubmissionResponse object
    """
    # In a real implementation, we would:
    # 1. Verify that the task exists and is assigned to the user
    # 2. Process the user's response
    # 3. Validate the response for quality
    # 4. Store the response in the database
    # 5. Update the user's profile based on the response
    # 6. Return a reward to the user
    
    # Get the task details from Redis
    task_key = f"task:{task_id}"
    task_json = await redis.get(task_key)
    
    if not task_json:
        # Task not found or expired
        return TaskSubmissionResponse(
            success=False,
            reward=Reward(type="none"),
            quality_score=0.0,
            next_task_available=True,
        )
    
    task_data = json.loads(task_json)
    
    # Validate the label quality
    validation_result = await validate_label_quality(
        db=db,
        redis=redis,
        task_id=task_id,
        session_id=submission.session_id,
        publisher_id=submission.publisher_id,
        response=submission.response,
        time_spent_ms=submission.time_spent_ms,
        task_type=task_data.get("task_type", "vqa"),
        validation_type="golden_set" if task_data.get("golden_set", False) else "consensus",
    )
    
    # Calculate reward based on quality
    reward_duration = 3600  # 1 hour content access by default
    if validation_result.quality_score >= 0.9:
        reward_duration = 7200  # 2 hours for high quality
    elif validation_result.quality_score >= 0.8:
        reward_duration = 5400  # 1.5 hours for good quality
    elif validation_result.quality_score >= 0.7:
        reward_duration = 3600  # 1 hour for acceptable quality
    else:
        reward_duration = 1800  # 30 minutes for poor quality
    
    # Store the submission in Redis (in a real system, would be in the database)
    submission_key = f"submission:{task_id}"
    await redis.set(submission_key, json.dumps({
        "task_id": task_id,
        "session_id": submission.session_id,
        "publisher_id": submission.publisher_id,
        "response": submission.response,
        "time_spent_ms": submission.time_spent_ms,
        "quality_score": validation_result.quality_score,
        "submitted_at": datetime.now().isoformat(),
    }), ex=86400)  # 24 hour expiration
    
    # Increment user task completion counter
    await redis.incr(f"user:tasks_completed:{submission.session_id}")
    
    # Check if more tasks are available
    next_task_available = True
    
    return TaskSubmissionResponse(
        success=True,
        reward=Reward(
            type="content_access",
            duration_seconds=reward_duration,
        ),
        quality_score=validation_result.quality_score,
        next_task_available=next_task_available,
    )

async def get_task_batch(
    db: AsyncSession,
    redis: Redis,
    publisher_id: str,
    count: int = 10,
    language: Optional[str] = None,
    category: Optional[str] = None,
    complexity: Optional[str] = None,
) -> TaskBatchResponse:
    """
    Get a batch of tasks for a publisher.
    
    Args:
        db: Database session
        redis: Redis connection
        publisher_id: Publisher ID
        count: Number of tasks to retrieve
        language: Language filter
        category: Category filter
        complexity: Complexity filter
        
    Returns:
        A TaskBatchResponse object
    """
    # In a real implementation, we would:
    # 1. Verify that the publisher has permission to get task batches
    # 2. Query the database for suitable tasks based on filters
    # 3. Create a batch of tasks
    
    # Convert complexity string to numeric range
    complexity_level = 1
    if complexity == "medium":
        complexity_level = 2
    elif complexity == "high":
        complexity_level = 3
    
    # Create a batch of mock tasks
    tasks = []
    for i in range(count):
        task_id = str(uuid.uuid4())
        tasks.append(TaskSummary(
            task_id=task_id,
            task_type="vqa",
            content=TaskContent(
                image_url=f"https://storage.hotlabel.io/samples/image{i}.jpg",
                question="What color is the car in this image?",
            ),
            options=["Red", "Blue", "Green", "Yellow"],
            complexity_level=complexity_level,
        ))
    
    # Store the batch in Redis
    batch_id = f"batch_{int(datetime.now().timestamp())}"
    batch_key = f"batch:{batch_id}"
    await redis.set(batch_key, json.dumps({
        "batch_id": batch_id,
        "publisher_id": publisher_id,
        "tasks": [task.dict() for task in tasks],
        "created_at": datetime.now().isoformat(),
    }), ex=3600)  # 1 hour expiration
    
    return TaskBatchResponse(
        batch_id=batch_id,
        tasks=tasks,
        expires_at=datetime.now() + timedelta(minutes=30),
    )
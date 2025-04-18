from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
from redis.asyncio import Redis

from api.db.session import get_db, get_redis
from api.dependencies import get_sdk_auth
from api.models.task import (
    TaskResponse,
    TaskBatchResponse,
    TaskSubmissionRequest,
    TaskSubmissionResponse,
)
from api.services.task_management import (
    get_next_task,
    submit_task_result,
    get_task_batch,
)

router = APIRouter()

@router.get("/next", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def get_next_task_for_user(
    session_id: str,
    publisher_id: str,
    language: Optional[str] = None,
    website_category: Optional[str] = None,
    previous_task_id: Optional[str] = None,
    auth: Dict[str, Any] = Depends(get_sdk_auth),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
    Retrieve the next appropriate labeling task for a user based on their profile and context.
    """
    # Verify that the publisher_id in the query matches the authenticated publisher_id
    if publisher_id != auth["publisher_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_parameter",
                "message": "Publisher ID in query does not match authenticated publisher",
            }
        )
    
    # Verify that the session_id matches the authenticated session_id
    if session_id != auth["session_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_parameter",
                "message": "Session ID in query does not match authenticated session",
            }
        )
    
    # Get the next task for the user
    task = await get_next_task(
        db=db,
        redis=redis,
        session_id=session_id,
        publisher_id=publisher_id,
        language=language,
        website_category=website_category,
        previous_task_id=previous_task_id,
    )
    
    # If no task is available, return 204 No Content
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail={
                "code": "no_task_available",
                "message": "No tasks available at this time",
            }
        )
    
    return task

@router.post("/{task_id}/submit", response_model=TaskSubmissionResponse)
async def submit_task_result_for_user(
    task_id: str = Path(..., description="The unique identifier of the task"),
    submission: TaskSubmissionRequest = ...,
    auth: Dict[str, Any] = Depends(get_sdk_auth),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
    Submit a user's response to a labeling task.
    """
    # Verify that the publisher_id in the submission matches the authenticated publisher_id
    if submission.publisher_id != auth["publisher_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_parameter",
                "message": "Publisher ID in submission does not match authenticated publisher",
            }
        )
    
    # Verify that the session_id in the submission matches the authenticated session_id
    if submission.session_id != auth["session_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_parameter",
                "message": "Session ID in submission does not match authenticated session",
            }
        )
    
    # Submit the task result
    result = await submit_task_result(
        db=db,
        redis=redis,
        task_id=task_id,
        submission=submission,
    )
    
    return result

@router.get("/batch", response_model=TaskBatchResponse)
async def get_tasks_batch(
    publisher_id: str,
    count: Optional[int] = Query(10, ge=1, le=100),
    language: Optional[str] = None,
    category: Optional[str] = None,
    complexity: Optional[str] = Query(None, regex="^(low|medium|high)$"),
    auth: Dict[str, Any] = Depends(get_sdk_auth),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
    For publishers with batch processing needs, retrieves multiple tasks at once.
    """
    # Verify that the publisher_id in the query matches the authenticated publisher_id
    if publisher_id != auth["publisher_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_parameter",
                "message": "Publisher ID in query does not match authenticated publisher",
            }
        )
    
    # Get a batch of tasks
    batch = await get_task_batch(
        db=db,
        redis=redis,
        publisher_id=publisher_id,
        count=count,
        language=language,
        category=category,
        complexity=complexity,
    )
    
    # If no tasks are available, return 204 No Content
    if not batch.tasks:
        raise HTTPException(
            status_code=status.HTTP_204_NO_CONTENT,
            detail={
                "code": "no_tasks_available",
                "message": "No tasks available matching criteria",
            }
        )
    
    return batch
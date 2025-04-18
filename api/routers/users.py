from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from redis.asyncio import Redis

from api.db.session import get_db, get_redis
from api.dependencies import get_sdk_auth, get_optional_sdk_auth
from api.models.user import (
    SessionInitRequest,
    SessionInitResponse,
    ProfileUpdateRequest,
    ProfileUpdateResponse,
    UserStatsResponse,
)
from api.services.user_profiling import (
    initialize_user_session,
    update_user_profile,
    get_user_statistics,
)

router = APIRouter()

@router.post("/sessions", response_model=SessionInitResponse, status_code=status.HTTP_201_CREATED)
async def init_user_session(
    session_request: SessionInitRequest,
    auth: Dict[str, Any] = Depends(get_optional_sdk_auth),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
    Initialize a new user session and create a temporary profile.
    """
    # Create a new session
    session = await initialize_user_session(
        db=db,
        redis=redis,
        session_request=session_request,
    )
    
    return session

@router.patch("/sessions/{session_id}/profile", response_model=ProfileUpdateResponse)
async def update_profile(
    session_id: str = Path(..., description="The session identifier"),
    profile_update: ProfileUpdateRequest = ...,
    auth: Dict[str, Any] = Depends(get_sdk_auth),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
    Update a user's profile based on their interaction history.
    """
    # Verify that the profile_update publisher_id matches the authenticated publisher_id
    if profile_update.publisher_id != auth["publisher_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_parameter",
                "message": "Publisher ID in profile update does not match authenticated publisher",
            }
        )
    
    # Verify that the session_id in path matches the authenticated session_id
    if session_id != auth["session_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_parameter",
                "message": "Session ID in path does not match authenticated session",
            }
        )
    
    # Update the user profile
    updated_profile = await update_user_profile(
        db=db,
        redis=redis,
        session_id=session_id,
        profile_update=profile_update,
    )
    
    if updated_profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "resource_not_found",
                "message": "Session not found",
            }
        )
    
    return updated_profile

@router.get("/sessions/{session_id}/statistics", response_model=UserStatsResponse)
async def get_user_stats(
    session_id: str = Path(..., description="The session identifier"),
    publisher_id: str = ...,
    auth: Dict[str, Any] = Depends(get_sdk_auth),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
    Retrieve statistics about a user's contributions and performance.
    """
    # Verify that the publisher_id in query matches the authenticated publisher_id
    if publisher_id != auth["publisher_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_parameter",
                "message": "Publisher ID in query does not match authenticated publisher",
            }
        )
    
    # Verify that the session_id in path matches the authenticated session_id
    if session_id != auth["session_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_parameter",
                "message": "Session ID in path does not match authenticated session",
            }
        )
    
    # Get the user statistics
    stats = await get_user_statistics(
        db=db,
        redis=redis,
        session_id=session_id,
        publisher_id=publisher_id,
    )
    
    if stats is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "resource_not_found",
                "message": "Session not found",
            }
        )
    
    return stats
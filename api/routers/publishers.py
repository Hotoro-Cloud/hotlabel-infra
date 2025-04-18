from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from datetime import datetime
from redis.asyncio import Redis

from api.db.session import get_db, get_redis
from api.dependencies import get_token_header
from api.models.publisher import (
    PublisherRegistrationRequest,
    PublisherRegistrationResponse,
    PublisherStatisticsResponse,
    ConfigurationUpdateRequest,
    ConfigurationUpdateResponse,
    IntegrationCodeResponse,
    WebhookConfigRequest,
    WebhookConfigResponse,
)
from api.services.publisher_management import (
    get_publisher_by_id,
    register_publisher,
    get_publisher_statistics,
    update_publisher_configuration,
    generate_integration_code,
    configure_webhook,
)

router = APIRouter()

@router.post("", response_model=PublisherRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_new_publisher(
    registration: PublisherRegistrationRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
    Register a new publisher with the HotLabel platform.
    """
    # Check if a publisher with the same website already exists
    # In a real implementation, we would query the database
    
    # Register the publisher
    response = await register_publisher(
        db=db,
        redis=redis,
        registration=registration,
    )
    
    return response

@router.get("/{publisher_id}/statistics", response_model=PublisherStatisticsResponse)
async def get_statistics(
    publisher_id: str = Path(..., description="The publisher's unique identifier"),
    start_date: Optional[str] = Query(None, description="Start date for metrics (ISO 8601 format)"),
    end_date: Optional[str] = Query(None, description="End date for metrics (ISO 8601 format)"),
    granularity: str = Query("daily", regex="^(hourly|daily|weekly|monthly)$"),
    auth: Dict[str, Any] = Depends(get_token_header),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve performance statistics for a publisher.
    """
    # Verify that the publisher_id matches the authenticated publisher or is an admin
    if publisher_id != auth["publisher_id"] and not auth.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "permission_denied",
                "message": "You do not have permission to access statistics for this publisher",
            }
        )
    
    # Parse dates
    parsed_start_date = None
    parsed_end_date = None
    
    if start_date:
        try:
            parsed_start_date = datetime.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "invalid_parameter",
                    "message": "Invalid start_date format",
                }
            )
    
    if end_date:
        try:
            parsed_end_date = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "invalid_parameter",
                    "message": "Invalid end_date format",
                }
            )
    
    # Get publisher statistics
    statistics = await get_publisher_statistics(
        db=db,
        publisher_id=publisher_id,
        start_date=parsed_start_date,
        end_date=parsed_end_date,
        granularity=granularity,
    )
    
    return statistics

@router.patch("/{publisher_id}/configuration", response_model=ConfigurationUpdateResponse)
async def update_configuration(
    publisher_id: str = Path(..., description="The publisher's unique identifier"),
    config_update: ConfigurationUpdateRequest = ...,
    auth: Dict[str, Any] = Depends(get_token_header),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
    Update a publisher's configuration settings.
    """
    # Verify that the publisher_id matches the authenticated publisher or is an admin
    if publisher_id != auth["publisher_id"] and not auth.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "permission_denied",
                "message": "You do not have permission to update configuration for this publisher",
            }
        )
    
    # Check if the publisher exists
    publisher = await get_publisher_by_id(db, publisher_id)
    if not publisher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "resource_not_found",
                "message": "Publisher not found",
            }
        )
    
    # Update the configuration
    config_response = await update_publisher_configuration(
        db=db,
        redis=redis,
        publisher_id=publisher_id,
        config_update=config_update,
    )
    
    return config_response

@router.get("/{publisher_id}/integration-code", response_model=IntegrationCodeResponse)
async def get_integration_code(
    publisher_id: str = Path(..., description="The publisher's unique identifier"),
    platform: str = Query("custom", description="Target platform (wordpress, custom, react, shopify, wix)"),
    include_comments: bool = Query(True, description="Whether to include explanatory comments in the code"),
    auth: Dict[str, Any] = Depends(get_token_header),
    db: AsyncSession = Depends(get_db),
):
    """
    Generate integration code snippets for different platforms.
    """
    # Verify that the publisher_id matches the authenticated publisher or is an admin
    if publisher_id != auth["publisher_id"] and not auth.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "permission_denied",
                "message": "You do not have permission to access integration code for this publisher",
            }
        )
    
    # Check if the publisher exists
    publisher = await get_publisher_by_id(db, publisher_id)
    if not publisher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "resource_not_found",
                "message": "Publisher not found",
            }
        )
    
    # Generate integration code
    integration_code = await generate_integration_code(
        db=db,
        publisher_id=publisher_id,
        platform=platform,
        include_comments=include_comments,
    )
    
    return integration_code

@router.post("/{publisher_id}/webhooks", response_model=WebhookConfigResponse)
async def configure_publisher_webhook(
    publisher_id: str = Path(..., description="The publisher's unique identifier"),
    webhook_config: WebhookConfigRequest = ...,
    auth: Dict[str, Any] = Depends(get_token_header),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    """
    Configure webhook endpoints for a publisher.
    """
    # Verify that the publisher_id matches the authenticated publisher or is an admin
    if publisher_id != auth["publisher_id"] and not auth.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "permission_denied",
                "message": "You do not have permission to configure webhooks for this publisher",
            }
        )
    
    # Check if the publisher exists
    publisher = await get_publisher_by_id(db, publisher_id)
    if not publisher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "resource_not_found",
                "message": "Publisher not found",
            }
        )
    
    # Configure the webhook
    webhook_response = await configure_webhook(
        db=db,
        redis=redis,
        publisher_id=publisher_id,
        webhook_config=webhook_config,
    )
    
    return webhook_response
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from api.models.publisher import (
    PublisherRegistrationRequest,
    PublisherRegistrationResponse,
    PublisherStatisticsResponse,
    ImpressionMetrics,
    RevenueMetrics,
    UserMetrics,
    TimeSeriesEntry,
    ConfigurationUpdateRequest,
    ConfigurationUpdateResponse,
    IntegrationCodeResponse,
    WebhookConfigRequest,
    WebhookConfigResponse,
)
from api.config import settings

async def get_publisher_by_id(
    db: AsyncSession,
    publisher_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Get a publisher by ID.
    
    Args:
        db: Database session
        publisher_id: Publisher ID
        
    Returns:
        Publisher data or None if not found
    """
    # In a real implementation, we would query the database
    # For demonstration purposes, we'll create a mock publisher
    
    # Mock data - in production would come from database
    if publisher_id.startswith("pub_"):
        return {
            "publisher_id": publisher_id,
            "company_name": "Example Media Group",
            "website_url": "https://example.com",
            "contact_email": "integration@example.com",
            "api_key": "pk_live_" + publisher_id[4:],
            "active": True,
            "created_at": datetime.now() - timedelta(days=30),
        }
    
    return None

async def register_publisher(
    db: AsyncSession,
    redis: Redis,
    registration: PublisherRegistrationRequest,
) -> PublisherRegistrationResponse:
    """
    Register a new publisher with the HotLabel platform.
    
    Args:
        db: Database session
        redis: Redis connection
        registration: Publisher registration request
        
    Returns:
        A PublisherRegistrationResponse object
    """
    # Generate a new publisher ID
    publisher_id = f"pub_{uuid.uuid4().hex[:10]}"
    
    # Generate an API key
    api_key = f"pk_live_{uuid.uuid4().hex[:16]}"
    
    # In a real implementation, we would:
    # 1. Validate the registration data
    # 2. Create a new publisher in the database
    # 3. Generate integration credentials
    
    # Store the publisher in Redis (for demo purposes)
    publisher_key = f"publisher:{publisher_id}"
    await redis.set(publisher_key, json.dumps({
        "publisher_id": publisher_id,
        "company_name": registration.company_name,
        "website_url": registration.website_url,
        "contact_email": registration.contact_email,
        "contact_name": registration.contact_name,
        "website_categories": registration.website_categories,
        "estimated_monthly_traffic": registration.estimated_monthly_traffic,
        "integration_platform": registration.integration_platform,
        "preferred_task_types": registration.preferred_task_types,
        "api_key": api_key,
        "created_at": datetime.now().isoformat(),
    }), ex=2592000)  # 30 day expiration (for demo)
    
    # Create SDK snippet based on the publisher ID
    sdk_snippet = f'<script src="{settings.SDK_CDN_BASE_URL}/{publisher_id}.js"></script>'
    
    return PublisherRegistrationResponse(
        publisher_id=publisher_id,
        api_key=api_key,
        dashboard_url=f"https://dashboard.hotlabel.io/publishers/{publisher_id}",
        integration_guide_url=f"https://docs.hotlabel.io/integration/{registration.integration_platform}",
        sdk_snippet=sdk_snippet,
    )

async def get_publisher_statistics(
    db: AsyncSession,
    publisher_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    granularity: str = "daily",
) -> PublisherStatisticsResponse:
    """
    Get statistics for a publisher.
    
    Args:
        db: Database session
        publisher_id: Publisher ID
        start_date: Start date for statistics
        end_date: End date for statistics
        granularity: Time granularity (hourly, daily, weekly, monthly)
        
    Returns:
        A PublisherStatisticsResponse object
    """
    # Set default dates if not provided
    if not end_date:
        end_date = datetime.now()
    if not start_date:
        start_date = end_date - timedelta(days=7)
    
    # In a real implementation, we would query the database for publisher statistics
    # For demonstration purposes, we'll create mock statistics
    
    # Create mock impression metrics
    impression_metrics = ImpressionMetrics(
        total_impressions=125400,
        task_displays=45200,
        task_completions=32150,
        completion_rate=0.71,
    )
    
    # Create mock revenue metrics
    revenue_metrics = RevenueMetrics(
        total_revenue=642.75,
        cpm=5.12,
        estimated_traditional_ad_revenue=125.40,
        revenue_uplift_percentage=412.56,
    )
    
    # Create mock user metrics
    user_metrics = UserMetrics(
        unique_users=28450,
        returning_users=12350,
        average_tasks_per_user=1.13,
    )
    
    # Create mock time series data
    time_series = []
    days = (end_date - start_date).days + 1
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        time_series.append(TimeSeriesEntry(
            date=current_date.date().isoformat(),
            impressions=17000 + (i * 200),  # Increasing trend
            completions=4500 + (i * 50),    # Increasing trend
            revenue=90.0 + (i * 2.5),       # Increasing trend
        ))
    
    return PublisherStatisticsResponse(
        period={
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        },
        impression_metrics=impression_metrics,
        revenue_metrics=revenue_metrics,
        user_metrics=user_metrics,
        time_series=time_series,
    )

async def update_publisher_configuration(
    db: AsyncSession,
    redis: Redis,
    publisher_id: str,
    config_update: ConfigurationUpdateRequest,
) -> ConfigurationUpdateResponse:
    """
    Update a publisher's configuration settings.
    
    Args:
        db: Database session
        redis: Redis connection
        publisher_id: Publisher ID
        config_update: Configuration update request
        
    Returns:
        A ConfigurationUpdateResponse object
    """
    # In a real implementation, we would:
    # 1. Validate the configuration update
    # 2. Update the publisher's configuration in the database
    
    # Get the current publisher configuration
    publisher_key = f"publisher:{publisher_id}"
    publisher_json = await redis.get(publisher_key)
    
    if not publisher_json:
        return ConfigurationUpdateResponse(
            success=False,
            updated_at=datetime.now().isoformat(),
            effective_from=datetime.now().isoformat(),
            configuration_version=0,
        )
    
    publisher_data = json.loads(publisher_json)
    
    # Update the configuration
    if not publisher_data.get("configuration"):
        publisher_data["configuration"] = {}
    
    # Apply the updates
    if config_update.appearance:
        publisher_data["configuration"]["appearance"] = config_update.appearance.dict()
    
    if config_update.behavior:
        publisher_data["configuration"]["behavior"] = config_update.behavior.dict()
    
    if config_update.task_preferences:
        publisher_data["configuration"]["task_preferences"] = config_update.task_preferences.dict()
    
    if config_update.rewards:
        publisher_data["configuration"]["rewards"] = config_update.rewards.dict()
    
    # Increment configuration version
    current_version = publisher_data.get("configuration_version", 0)
    new_version = current_version + 1
    publisher_data["configuration_version"] = new_version
    
    # Update the publisher in Redis
    await redis.set(publisher_key, json.dumps(publisher_data), ex=2592000)  # 30 day expiration
    
    # Calculate effective from time (5 minutes from now)
    effective_from = datetime.now() + timedelta(minutes=5)
    
    return ConfigurationUpdateResponse(
        success=True,
        updated_at=datetime.now().isoformat(),
        effective_from=effective_from.isoformat(),
        configuration_version=new_version,
    )

async def generate_integration_code(
    db: AsyncSession,
    publisher_id: str,
    platform: str = "custom",
    include_comments: bool = True,
) -> IntegrationCodeResponse:
    """
    Generate integration code snippets for different platforms.
    
    Args:
        db: Database session
        publisher_id: Publisher ID
        platform: Target platform (wordpress, custom, etc.)
        include_comments: Whether to include explanatory comments
        
    Returns:
        An IntegrationCodeResponse object
    """
    # In a real implementation, we would:
    # 1. Validate that the publisher exists
    # 2. Retrieve the publisher's configuration
    # 3. Generate platform-specific code snippets
    
    # Base SDK URL
    sdk_url = f"{settings.SDK_CDN_BASE_URL}/{publisher_id}.js"
    
    # Generate code snippets based on the platform
    code_snippets = {}
    installation_steps = []
    
    if platform == "wordpress":
        code_snippets["header"] = f'<script src="{sdk_url}"></script>'
        code_snippets["body"] = '<div id="hotlabel-container"></div>\n<script>\nHotLabel.init({\n  containerId: "hotlabel-container",\n  appearance: {\n    theme: "light",\n    primaryColor: "#3366FF"\n  }\n});\n</script>'
        
        installation_steps = [
            "Install the HotLabel WordPress plugin from the WordPress plugin directory",
            f"Navigate to Settings > HotLabel in your WordPress admin",
            f"Enter your Publisher ID: {publisher_id}",
            "Save your settings and the integration is complete",
        ]
    
    elif platform == "react":
        code_snippets["installation"] = f"npm install hotlabel-react"
        code_snippets["component"] = 'import { HotLabel } from "hotlabel-react";\n\nfunction App() {\n  return (\n    <div className="App">\n      <HotLabel\n        publisherId="{publisher_id}"\n        theme="light"\n        primaryColor="#3366FF"\n      />\n    </div>\n  );\n}\n\nexport default App;'
        
        installation_steps = [
            "Install the HotLabel React component",
            "Import and use the HotLabel component in your application",
            "Configure the component with your Publisher ID",
        ]
    
    elif platform == "custom":
        code_snippets["header"] = f'<script src="{sdk_url}"></script>'
        code_snippets["body"] = '<div id="hotlabel-container"></div>\n<script>\ndocument.addEventListener("DOMContentLoaded", function() {\n  HotLabel.init({\n    containerId: "hotlabel-container",\n    appearance: {\n      theme: "light",\n      primaryColor: "#3366FF"\n    },\n    behavior: {\n      taskDisplayFrequency: 300,\n      maxTasksPerSession: 5\n    }\n  });\n});\n</script>'
        
        installation_steps = [
            "Add the HotLabel script to your HTML head section",
            "Create a container div where the HotLabel widget will appear",
            "Initialize HotLabel with your configuration options",
        ]
    
    # Add comments if requested
    if include_comments and platform == "custom":
        code_snippets["header"] = '<!-- Add this script to your page head -->\n' + code_snippets["header"]
        code_snippets["body"] = '<!-- Add this where you want the HotLabel widget to appear -->\n' + code_snippets["body"]
    
    return IntegrationCodeResponse(
        platform=platform,
        code_snippets=code_snippets,
        installation_steps=installation_steps,
        documentation_url=f"https://docs.hotlabel.io/integration/{platform}",
    )

async def configure_webhook(
    db: AsyncSession,
    redis: Redis,
    publisher_id: str,
    webhook_config: WebhookConfigRequest,
) -> WebhookConfigResponse:
    """
    Configure webhook endpoints for a publisher.
    
    Args:
        db: Database session
        redis: Redis connection
        publisher_id: Publisher ID
        webhook_config: Webhook configuration request
        
    Returns:
        A WebhookConfigResponse object
    """
    # Generate a webhook ID
    webhook_id = f"wh_{uuid.uuid4().hex[:10]}"
    
    # In a real implementation, we would:
    # 1. Validate the webhook configuration
    # 2. Store the webhook configuration in the database
    
    # Store the webhook in Redis
    webhook_key = f"webhook:{publisher_id}:{webhook_id}"
    await redis.set(webhook_key, json.dumps({
        "webhook_id": webhook_id,
        "publisher_id": publisher_id,
        "endpoint_url": webhook_config.endpoint_url,
        "secret_key": webhook_config.secret_key,
        "events": webhook_config.events,
        "active": webhook_config.active,
        "created_at": datetime.now().isoformat(),
    }), ex=2592000)  # 30 day expiration
    
    return WebhookConfigResponse(
        webhook_id=webhook_id,
        status="active" if webhook_config.active else "inactive",
        test_event_url=f"https://api.hotlabel.io/v1/publishers/{publisher_id}/webhooks/{webhook_id}/test",
    )
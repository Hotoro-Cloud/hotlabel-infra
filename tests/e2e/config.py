import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base URLs
KONG_BASE_URL = os.getenv("KONG_BASE_URL", "http://localhost:8000")

# Service URLs
USERS_SERVICE_URL = f"{KONG_BASE_URL}/api/v1/users"
TASKS_SERVICE_URL = f"{KONG_BASE_URL}/api/v1/tasks"
QA_SERVICE_URL = f"{KONG_BASE_URL}/api/v1/quality"
PUBLISHERS_SERVICE_URL = f"{KONG_BASE_URL}/api/v1/publishers"

# Test Configuration
TEST_TIMEOUT = int(os.getenv("TEST_TIMEOUT", "30"))  # seconds
RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "3"))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", "5"))  # seconds

# Test Data
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User",
    "is_active": True,
    "is_superuser": False,
}

TEST_PROFILE = {
    "bio": "Test bio",
    "location": "Test location",
    "timezone": "UTC",
}

TEST_EXPERTISE = {
    "domain": "Test Domain",
    "level": "Expert",
    "years_of_experience": 5,
}

TEST_DATASET = {
    "name": "Test Dataset",
    "description": "Test dataset description",
    "type": "text",
    "status": "active",
}

TEST_TASK = {
    "title": "Test Task",
    "description": "Test task description",
    "dataset_id": None,  # Will be set during test
    "status": "pending",
    "priority": "medium",
}

TEST_VALIDATION = {
    "task_id": None,  # Will be set during test
    "validator_id": None,  # Will be set during test
    "status": "approved",
    "comments": "Test validation comments",
}

# Headers
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
} 
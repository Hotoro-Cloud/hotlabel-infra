import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from config import (
    TEST_DATASET,
    TEST_EXPERTISE,
    TEST_PROFILE,
    TEST_TASK,
    TEST_USER,
    TEST_VALIDATION,
    USERS_SERVICE_URL,
    TASKS_SERVICE_URL,
    QA_SERVICE_URL,
)
from utils import APIClient, cleanup_test_data, wait_for_service


@pytest.fixture(scope="session")
def users_client():
    return APIClient(USERS_SERVICE_URL)


@pytest.fixture(scope="session")
def tasks_client():
    return APIClient(TASKS_SERVICE_URL)


@pytest.fixture(scope="session")
def qa_client():
    return APIClient(QA_SERVICE_URL)


@pytest.fixture(scope="session")
def test_user(users_client):
    # Create test user
    user_data = users_client.post("/users", TEST_USER)
    yield user_data["data"]
    # Cleanup
    cleanup_test_data(users_client, "/users", user_data["data"]["id"])


@pytest.fixture(scope="session")
def test_profile(users_client, test_user):
    # Create test profile
    profile_data = TEST_PROFILE.copy()
    profile_data["user_id"] = test_user["id"]
    profile = users_client.post("/profiles", profile_data)
    yield profile["data"]
    # Cleanup
    cleanup_test_data(users_client, "/profiles", profile["data"]["id"])


@pytest.fixture(scope="session")
def test_expertise(users_client, test_user):
    # Create test expertise
    expertise_data = TEST_EXPERTISE.copy()
    expertise_data["user_id"] = test_user["id"]
    expertise = users_client.post("/expertise", expertise_data)
    yield expertise["data"]
    # Cleanup
    cleanup_test_data(users_client, "/expertise", expertise["data"]["id"])


@pytest.fixture(scope="session")
def test_dataset(tasks_client):
    # Create test dataset
    dataset = tasks_client.post("/datasets", TEST_DATASET)
    yield dataset["data"]
    # Cleanup
    cleanup_test_data(tasks_client, "/datasets", dataset["data"]["id"])


@pytest.fixture(scope="session")
def test_task(tasks_client, test_dataset):
    # Create test task
    task_data = TEST_TASK.copy()
    task_data["dataset_id"] = test_dataset["id"]
    task = tasks_client.post("/tasks", task_data)
    yield task["data"]
    # Cleanup
    cleanup_test_data(tasks_client, "/tasks", task["data"]["id"])


@pytest.fixture(scope="session")
def test_validation(qa_client, test_task, test_user):
    # Create test validation
    validation_data = TEST_VALIDATION.copy()
    validation_data["task_id"] = test_task["id"]
    validation_data["validator_id"] = test_user["id"]
    validation = qa_client.post("/validation/tasks", validation_data)
    yield validation["data"]
    # Cleanup
    cleanup_test_data(qa_client, "/validation/tasks", validation["data"]["id"])


def test_services_health():
    """Test that all services are healthy."""
    assert wait_for_service(f"{USERS_SERVICE_URL}/health")
    assert wait_for_service(f"{TASKS_SERVICE_URL}/health")
    assert wait_for_service(f"{QA_SERVICE_URL}/health")


def test_user_workflow(users_client, test_user, test_profile, test_expertise):
    """Test the complete user workflow."""
    # Get user details
    user = users_client.get(f"/users/{test_user['id']}")
    assert user["data"]["email"] == TEST_USER["email"]

    # Get profile details
    profile = users_client.get(f"/profiles/{test_profile['id']}")
    assert profile["data"]["bio"] == TEST_PROFILE["bio"]

    # Get expertise details
    expertise = users_client.get(f"/expertise/{test_expertise['id']}")
    assert expertise["data"]["domain"] == TEST_EXPERTISE["domain"]

    # Get user statistics
    stats = users_client.get(f"/statistics/users/{test_user['id']}")
    assert "data" in stats


def test_task_workflow(tasks_client, test_dataset, test_task):
    """Test the complete task workflow."""
    # Get dataset details
    dataset = tasks_client.get(f"/datasets/{test_dataset['id']}")
    assert dataset["data"]["name"] == TEST_DATASET["name"]

    # Get task details
    task = tasks_client.get(f"/tasks/{test_task['id']}")
    assert task["data"]["title"] == TEST_TASK["title"]


def test_qa_workflow(qa_client, test_task, test_validation):
    """Test the complete QA workflow."""
    # Get task validation
    validation = qa_client.get(f"/validation/tasks/{test_validation['id']}")
    assert validation["data"]["status"] == TEST_VALIDATION["status"]

    # Get task metrics
    metrics = qa_client.get(f"/metrics/tasks/{test_task['id']}")
    assert "data" in metrics

    # Get consensus results
    consensus = qa_client.get(f"/consensus/tasks/{test_task['id']}")
    assert "data" in consensus


def test_end_to_end_workflow(
    users_client,
    tasks_client,
    qa_client,
    test_user,
    test_dataset,
    test_task,
    test_validation,
):
    """Test the complete end-to-end workflow."""
    # 1. Create and verify user
    user = users_client.get(f"/users/{test_user['id']}")
    assert user["data"]["email"] == TEST_USER["email"]

    # 2. Create and verify dataset
    dataset = tasks_client.get(f"/datasets/{test_dataset['id']}")
    assert dataset["data"]["name"] == TEST_DATASET["name"]

    # 3. Create and verify task
    task = tasks_client.get(f"/tasks/{test_task['id']}")
    assert task["data"]["title"] == TEST_TASK["title"]

    # 4. Create and verify validation
    validation = qa_client.get(f"/validation/tasks/{test_validation['id']}")
    assert validation["data"]["status"] == TEST_VALIDATION["status"]

    # 5. Get QA metrics and reports
    metrics = qa_client.get(f"/metrics/tasks/{test_task['id']}")
    assert "data" in metrics

    reports = qa_client.get("/reports/tasks")
    assert "data" in reports


def test_error_handling(users_client, tasks_client, qa_client):
    """Test error handling for invalid requests."""
    # Test invalid user ID
    with pytest.raises(Exception):
        users_client.get("/users/invalid-id")

    # Test invalid dataset ID
    with pytest.raises(Exception):
        tasks_client.get("/datasets/invalid-id")

    # Test invalid task ID
    with pytest.raises(Exception):
        qa_client.get("/validation/tasks/invalid-id")

    # Test invalid request body
    with pytest.raises(Exception):
        users_client.post("/users", {"invalid": "data"})

    # Test missing required fields
    with pytest.raises(Exception):
        tasks_client.post("/tasks", {"title": "Missing Required Fields"})


def test_concurrent_operations(users_client, tasks_client, qa_client, test_dataset):
    """Test concurrent operations across services."""
    def create_task():
        task_data = TEST_TASK.copy()
        task_data["dataset_id"] = test_dataset["id"]
        return tasks_client.post("/tasks", task_data)

    def create_validation(task_id):
        validation_data = TEST_VALIDATION.copy()
        validation_data["task_id"] = task_id
        return qa_client.post("/validation/tasks", validation_data)

    # Create multiple tasks concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        task_futures = [executor.submit(create_task) for _ in range(5)]
        tasks = [future.result()["data"] for future in task_futures]

    # Create validations for all tasks concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        validation_futures = [
            executor.submit(create_validation, task["id"]) for task in tasks
        ]
        validations = [future.result()["data"] for future in validation_futures]

    # Verify all tasks and validations were created
    assert len(tasks) == 5
    assert len(validations) == 5

    # Cleanup
    for task in tasks:
        cleanup_test_data(tasks_client, "/tasks", task["id"])
    for validation in validations:
        cleanup_test_data(qa_client, "/validation/tasks", validation["id"])


def test_rate_limiting(users_client):
    """Test rate limiting through Kong."""
    # Make rapid requests to trigger rate limiting
    start_time = time.time()
    requests_made = 0
    rate_limited = False

    while time.time() - start_time < 5:  # Try for 5 seconds
        try:
            users_client.get("/users")
            requests_made += 1
        except Exception as e:
            if "429" in str(e):  # Too Many Requests
                rate_limited = True
                break
        time.sleep(0.1)  # Small delay between requests

    assert rate_limited, "Rate limiting was not triggered"
    assert requests_made > 0, "No requests were made"


def test_request_id_tracking(users_client):
    """Test request ID tracking through Kong."""
    response = users_client.get("/users")
    assert "X-Request-ID" in response.headers
    assert response.headers["X-Request-ID"]  # Ensure it's not empty


def test_cors_headers(users_client):
    """Test CORS headers through Kong."""
    response = users_client.get("/users")
    assert "Access-Control-Allow-Origin" in response.headers
    assert response.headers["Access-Control-Allow-Origin"] == "*"


def test_service_dependencies(users_client, tasks_client, qa_client, test_user, test_dataset):
    """Test service dependencies and communication."""
    # Create a task that depends on user and dataset
    task_data = TEST_TASK.copy()
    task_data["dataset_id"] = test_dataset["id"]
    task_data["assignee_id"] = test_user["id"]
    task = tasks_client.post("/tasks", task_data)

    # Verify task was created with correct dependencies
    created_task = tasks_client.get(f"/tasks/{task['data']['id']}")
    assert created_task["data"]["dataset_id"] == test_dataset["id"]
    assert created_task["data"]["assignee_id"] == test_user["id"]

    # Cleanup
    cleanup_test_data(tasks_client, "/tasks", task["data"]["id"])


def test_data_consistency(users_client, tasks_client, qa_client, test_user, test_dataset):
    """Test data consistency across services."""
    # Create a task
    task_data = TEST_TASK.copy()
    task_data["dataset_id"] = test_dataset["id"]
    task = tasks_client.post("/tasks", task_data)

    # Create a validation
    validation_data = TEST_VALIDATION.copy()
    validation_data["task_id"] = task["data"]["id"]
    validation_data["validator_id"] = test_user["id"]
    validation = qa_client.post("/validation/tasks", validation_data)

    # Verify data consistency
    task_details = tasks_client.get(f"/tasks/{task['data']['id']}")
    validation_details = qa_client.get(f"/validation/tasks/{validation['data']['id']}")

    assert task_details["data"]["id"] == validation_details["data"]["task_id"]
    assert test_user["id"] == validation_details["data"]["validator_id"]

    # Cleanup
    cleanup_test_data(qa_client, "/validation/tasks", validation["data"]["id"])
    cleanup_test_data(tasks_client, "/tasks", task["data"]["id"]) 
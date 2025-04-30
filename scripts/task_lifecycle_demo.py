#!/usr/bin/env python3
"""
Task Lifecycle Demo

This script demonstrates the complete lifecycle of a task in the Hotlabel platform:
1. Provider registers and receives API key
2. Provider creates a task
3. Publisher registers and receives API key
4. Publisher receives the task
5. Publisher submits result for task
6. QA service receives task result and validates it
7. Final result is appended to task and is made available to provider
"""

import requests
import uuid
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import sys
import random
import os
import subprocess

# Configuration
KONG_URL = "http://localhost:8000"  # API Gateway URL
TASKS_API_URL = f"{KONG_URL}/api/v1/tasks"
PROVIDERS_API_URL = f"{KONG_URL}/api/v1/providers"
PUBLISHERS_API_URL = f"{KONG_URL}/api/v1/publishers"
QA_API_URL = f"{KONG_URL}/api/v1/qa"

# Direct service URLs (if needed for endpoints not exposed through Kong)
TASKS_SERVICE_URL = "http://localhost:8002"
PUBLISHERS_SERVICE_URL = "http://localhost:8004"
QA_SERVICE_URL = "http://localhost:8003"
USERS_SERVICE_URL = "http://localhost:8005"

# QA Service endpoints
VALIDATION_URL = f"{QA_SERVICE_URL}/api/v1/validation"
METRICS_URL = f"{QA_SERVICE_URL}/api/v1/metrics"
QA_API_KEY = "test_api_key_qa_service"  # QA service API key

def print_header(title: str) -> None:
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def print_step(step: str) -> None:
    """Print a step in the process"""
    print(f"\n--- {step} ---")

def print_response(response: requests.Response, title: str) -> None:
    """Print API response in a readable format"""
    print(f"\n=== {title} ===")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(f"Raw response text: {response.text}")
    print("-" * 50)


class TaskLifecycle:
    """Class to manage the task lifecycle demonstration"""
    
    def __init__(self):
        self.provider_id = None
        self.provider_api_key = None
        self.task_id = None
        self.publisher_id = None
        self.publisher_api_key = None
        self.result_id = None
        self.validation_id = None
        self.validator_id = None
        
    def register_provider(self) -> Dict[str, Any]:
        """Register a new provider"""
        print_step("STEP 1: Register a provider")
        
        provider_data = {
            "name": "Demo Provider",
            "contact_email": f"provider_{uuid.uuid4().hex[:8]}@example.com",
            "description": "A demo provider for task lifecycle testing",
            "website": "https://example.com/provider"
        }
        
        response = requests.post(PROVIDERS_API_URL, json=provider_data)
        print_response(response, "Provider Registration")
        
        if response.status_code >= 300:
            print("ERROR: Failed to register provider")
            sys.exit(1)
            
        result = response.json()
        self.provider_id = result["id"]
        self.provider_api_key = result["api_key"]
        
        print(f"Provider registered successfully!")
        print(f"Provider ID: {self.provider_id}")
        print(f"Provider API Key: {self.provider_api_key}")
        
        return result
        
    def create_task(self) -> Dict[str, Any]:
        """Create a new task as a provider"""
        print_step("STEP 2: Provider creates a task")
        
        task_data = {
            "title": "Demo Classification Task",
            "description": "A demo task for the task lifecycle demonstration",
            "provider_id": self.provider_id,
            "task_type": "vqa",  # Using a supported task type (Visual Question Answering)
            "content": {
                "image_url": "https://example.com/images/sample.jpg",
                "question": "What is in this image?"  # Required field for vqa task type
            },
            "language": "en",
            "category": "demo",
            "complexity_level": 2,
            "tags": ["demo", "classification", "lifecycle"],
            "options": {"demo_option": True},
            "time_estimate_seconds": 120,
            "expires_at": (datetime.utcnow() + timedelta(days=1)).isoformat(),
            "status": "pending"
        }
        
        headers = {"X-API-Key": self.provider_api_key}
        response = requests.post(TASKS_API_URL, json=task_data, headers=headers)
        print_response(response, "Task Creation")
        
        if response.status_code >= 300:
            print("ERROR: Failed to create task")
            sys.exit(1)
            
        result = response.json()
        self.task_id = result["id"]
        
        print(f"Task created successfully!")
        print(f"Task ID: {self.task_id}")
        
        return result
        
    def register_publisher(self) -> Dict[str, Any]:
        """Register a new publisher"""
        print_step("STEP 3: Register a publisher")
        
        publisher_data = {
            "name": "Demo Publisher",
            "email": f"publisher_{uuid.uuid4().hex[:8]}@example.com",
            "description": "A demo publisher for task lifecycle testing",
            "website": "https://example.com/publisher"
        }
        
        response = requests.post(PUBLISHERS_API_URL, json=publisher_data)
        print_response(response, "Publisher Registration")
        
        if response.status_code >= 300:
            print("ERROR: Failed to register publisher")
            sys.exit(1)
            
        result = response.json()
        self.publisher_id = result["id"]
        self.publisher_api_key = result["api_key"]
        
        print(f"Publisher registered successfully!")
        print(f"Publisher ID: {self.publisher_id}")
        print(f"Publisher API Key: {self.publisher_api_key}")
        
        return result
        
    def assign_task_to_publisher(self) -> Dict[str, Any]:
        """Assign the task to the publisher"""
        print_step("STEP 4a: Provider assigns task to publisher")
        
        assignment_data = {
            "publisher_id": self.publisher_id,
            "message": "Please complete this task for our demo"
        }
        
        headers = {"X-API-Key": self.provider_api_key}
        response = requests.post(
            f"{TASKS_API_URL}/{self.task_id}/assign", 
            json=assignment_data, 
            headers=headers
        )
        print_response(response, "Task Assignment")
        
        if response.status_code >= 300:
            print("ERROR: Failed to assign task to publisher")
            sys.exit(1)
            
        result = response.json()
        print("Task assigned successfully!")
        
        return result
        
    def publisher_gets_tasks(self) -> List[Dict[str, Any]]:
        """Publisher retrieves their assigned tasks"""
        print_step("STEP 4b: Publisher retrieves assigned tasks")
        
        headers = {"X-API-Key": self.publisher_api_key}
        response = requests.get(
            f"{PUBLISHERS_API_URL}/{self.publisher_id}/tasks", 
            headers=headers
        )
        print_response(response, "Publisher Tasks")
        
        if response.status_code >= 300:
            print("ERROR: Failed to retrieve publisher tasks")
            sys.exit(1)
            
        result = response.json()
        print(f"Retrieved {len(result)} tasks for publisher")
        
        return result
        
    def publisher_submits_result(self) -> Dict[str, Any]:
        """Publisher submits result for the task"""
        print_step("STEP 5: Publisher submits result for task")
        
        result_data = {
            "result": {
                "answer": "I can see a cat sitting on a windowsill",
                "confidence": 0.95
            },
            "quality_score": 0.95,
            "rejection_reason": None
        }
        
        headers = {"X-API-Key": self.publisher_api_key}
        response = requests.post(
            f"{TASKS_API_URL}/{self.task_id}/result", 
            json=result_data, 
            headers=headers
        )
        print_response(response, "Task Result Submission")
        
        if response.status_code >= 300:
            print("ERROR: Failed to submit task result")
            sys.exit(1)
            
        result = response.json()
        self.result_id = result.get("id") or self.task_id  # Some APIs might not return a separate result ID
        
        print(f"Task result submitted successfully!")
        print(f"Result ID: {self.result_id}")
        
        return result
    
    def create_validator(self) -> Dict[str, Any]:
        """Create a validator in the QA service"""
        print_step("STEP 7a: Create a validator in QA service")
        
        validator_data = {
            "name": "Demo Validator",
            "email": f"validator_{uuid.uuid4().hex[:8]}@example.com",
            "is_active": True
        }
        
        headers = {"X-API-Key": QA_API_KEY}
        response = requests.post(
            f"{QA_SERVICE_URL}/api/v1/admin/validators", 
            json=validator_data, 
            headers=headers
        )
        print_response(response, "Validator Creation")
        
        if response.status_code >= 300:
            print("ERROR: Failed to create validator")
            sys.exit(1)
            
        result = response.json()
        self.validator_id = result["id"]
        
        print(f"Validator created successfully!")
        print(f"Validator ID: {self.validator_id}")
        
        return result
    
    def qa_validates_result(self) -> Dict[str, Any]:
        """QA service validates the task result"""
        print_step("STEP 7b: QA service validates task result")
        
        validation_data = {
            "task_id": self.task_id,
            "result_id": self.result_id,
            "validator_id": self.validator_id,
            "response": {
                "class": "cat",
                "confidence": 1.0
            },
            "time_spent_ms": 5000
        }
        
        headers = {"X-API-Key": QA_API_KEY}
        response = requests.post(
            VALIDATION_URL, 
            json=validation_data, 
            headers=headers
        )
        print_response(response, "Task Validation")
        
        if response.status_code >= 300:
            print("ERROR: Failed to validate task result")
            sys.exit(1)
            
        result = response.json()
        self.validation_id = result["id"]
        
        print(f"Task result validated successfully!")
        print(f"Validation ID: {self.validation_id}")
        
        return result
    
    def qa_approves_validation(self) -> Dict[str, Any]:
        """QA service approves the validation"""
        print_step("STEP 7c: QA service approves the validation")
        
        update_data = {
            "status": "validated"
        }
        
        headers = {"X-API-Key": QA_API_KEY}
        response = requests.patch(
            f"{VALIDATION_URL}/{self.validation_id}/status", 
            json=update_data, 
            headers=headers
        )
        print_response(response, "Validation Approval")
        
        if response.status_code >= 300:
            print("ERROR: Failed to approve validation")
            sys.exit(1)
            
        result = response.json()
        print("Validation approved successfully!")
        
        return result
    
    def qa_creates_metrics(self) -> Dict[str, Any]:
        """QA service creates metrics for the validation"""
        print_step("STEP 7d: QA service creates metrics for validation")
        
        metrics_data = {
            "validation_id": self.validation_id,
            "task_id": self.task_id,
            "accuracy": 0.98,
            "precision": 0.95,
            "recall": 0.96,
            "f1_score": 0.955,
            "latency_ms": 150,
            "custom_metrics": {
                "confidence": 0.98,
                "difficulty": 2
            }
        }
        
        headers = {"X-API-Key": QA_API_KEY}
        response = requests.post(
            METRICS_URL, 
            json=metrics_data, 
            headers=headers
        )
        print_response(response, "Metrics Creation")
        
        if response.status_code >= 300:
            print("ERROR: Failed to create metrics")
            sys.exit(1)
            
        result = response.json()
        print("Metrics created successfully!")
        
        return result
    
    def provider_gets_task_with_results(self) -> Dict[str, Any]:
        """Provider retrieves the task with its validated results"""
        print_step("STEP 8: Provider retrieves finalized task with results")
        
        headers = {"X-API-Key": self.provider_api_key}
        response = requests.get(
            f"{TASKS_API_URL}/{self.task_id}", 
            headers=headers
        )
        print_response(response, "Task with Results")
        
        if response.status_code >= 300:
            print("ERROR: Failed to retrieve task with results")
            sys.exit(1)
            
        result = response.json()
        print("Task retrieved successfully with validation results!")
        
        # Also get the results through results endpoint
        response = requests.get(
            f"{TASKS_API_URL}/{self.task_id}/results", 
            headers=headers
        )
        print_response(response, "Task Results")
        
        return result

    def create_qa_task(self) -> Dict[str, Any]:
        """Create the task in the QA service database"""
        print_step("STEP 6a: Create task in QA service database")
        
        # For demo purposes, we'll use a simple approach by running the create_test_data.py script
        # In a production environment, there would be a proper API endpoint or message queue
        
        # Get the path to the script
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                 "../hotlabel-qa/scripts/create_test_data.py")
        
        # Run the script to create a task in the QA database
        print(f"Running script to create task in QA database...")
        
        try:
            # Use the task ID we already have
            # Note: In a real environment, the ID would need to match between services
            import_command = f"import os; os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@postgres:5432/hotlabel_qa'; from scripts.create_test_data import create_test_task_with_id; task_id = '{self.task_id}'; print(create_test_task_with_id(task_id));"
            
            # Run in the QA service container
            result = subprocess.run(
                ["docker", "exec", "hotlabel-qa", "python", "-c", import_command],
                capture_output=True,
                text=True
            )
            
            print(f"Script output: {result.stdout}")
            
            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                print("WARNING: Failed to create task in QA database, but continuing anyway...")
            else:
                print(f"Task created in QA database with ID: {self.task_id}")
                
        except Exception as e:
            print(f"WARNING: Error creating task in QA database: {str(e)}")
            print("Continuing with the workflow anyway...")
        
        return {"task_id": self.task_id}

def main():
    print_header("HOTLABEL TASK LIFECYCLE DEMONSTRATION")
    print("\nThis script demonstrates the complete task lifecycle across all Hotlabel services.")
    
    # Initialize our workflow manager
    workflow = TaskLifecycle()
    
    try:
        # Step 1: Provider Registration
        workflow.register_provider()
        
        # Step 2: Task Creation
        workflow.create_task()
        
        # Step 3: Publisher Registration
        workflow.register_publisher()
        
        # Step 4: Task Assignment and Retrieval
        workflow.assign_task_to_publisher()
        workflow.publisher_gets_tasks()
        
        # Step 5: Result Submission
        workflow.publisher_submits_result()
        
        # Step 6: Create task in QA database to enable validation
        workflow.create_qa_task()
        
        # Step 7: QA Service Validation
        workflow.create_validator()
        workflow.qa_validates_result()
        workflow.qa_approves_validation()
        workflow.qa_creates_metrics()
        
        # Step 8: Provider Retrieves Validated Results
        workflow.provider_gets_task_with_results()
        
        print_header("TASK LIFECYCLE DEMONSTRATION COMPLETED SUCCESSFULLY")
        
    except Exception as e:
        print(f"\nERROR: An exception occurred during the task lifecycle demonstration!")
        print(f"Error details: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
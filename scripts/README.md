# Hotlabel Infrastructure Scripts

This directory contains utility scripts for the Hotlabel platform.

## Task Lifecycle Demo

The `task_lifecycle_demo.py` script demonstrates the complete task lifecycle in the Hotlabel platform, including interactions between all services:

1. Provider registers and receives an API key
2. Provider creates a task
3. Publisher registers and receives an API key
4. Publisher receives and processes the task
5. Publisher submits a result for the task
6. QA service validates the task result
7. Final result is appended to the task and made available to the provider

### Prerequisites

- All Hotlabel services must be running locally (use `docker-compose -f docker-compose-local.yml up -d`)
- Python 3.8+ with the `requests` library installed

### Usage

Run the script from the hotlabel-infra directory:

```bash
# Make sure script is executable
chmod +x scripts/task_lifecycle_demo.py

# Run the script
./scripts/task_lifecycle_demo.py
```

The script will:
- Walk through each step of the task lifecycle
- Print detailed information about API requests and responses
- Track IDs and data needed at each step
- Provide a clear overview of how data flows between services

### Troubleshooting

If you encounter errors:

1. Ensure all services are running - check Docker containers with `docker-compose -f docker-compose-local.yml ps`
2. Verify the Kong API gateway is working properly - try accessing http://localhost:8000/health
3. Check individual service logs with `docker-compose -f docker-compose-local.yml logs [service_name]`
4. Ensure the database migrations have been applied for each service

## Other Scripts

(Add documentation for other scripts as they are created)

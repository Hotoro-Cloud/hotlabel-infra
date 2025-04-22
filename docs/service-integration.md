# Service Integration Guide

This guide explains how to integrate the different microservices with the HotLabel infrastructure.

## Overview

The HotLabel platform consists of four core microservices, each with its own responsibilities but integrated through common infrastructure components. Each service requires specific configuration for proper integration.

## General Integration Requirements

All services should implement:

1. **Health and Readiness Endpoints**
   - `/health` - Basic service health check
   - `/ready` - Detailed readiness check including database and Redis connections

2. **Standardized Environment Variables**
   - `DATABASE_URL` - PostgreSQL connection string
   - `REDIS_URL` - Redis connection string
   - `API_V1_STR` - API prefix
   - `SERVICE_NAME` - Name of the service

3. **Docker Configuration**
   - A properly configured Dockerfile
   - Service-specific docker-compose file
   - Support for infrastructure docker-compose file

## Quality Assurance Service Integration

### Connection Parameters

The Quality Assurance service connects to these resources:

| Resource | Connection Parameters |
| --- | --- |
| PostgreSQL | `postgresql://postgres:postgres@postgres:5432/hotlabel_qa` |
| Redis | `redis://redis:6379/2` |
| Task Service | `http://tasks:8000/api/v1` |
| User Service | `http://users:8000/api/v1` |
| Network | `hotlabel-network` |

### Kong API Gateway Integration

The Kong API Gateway routes requests to the QA service based on the URL path:

```yaml
services:
  - name: qa-service
    url: http://qa:8000
    routes:
      - name: qa-routes
        paths:
          - /api/v1/quality
```

### Monitoring Integration

The QA service exposes metrics endpoints for Prometheus:

- `/metrics` - Standard Prometheus metrics
- `/health` - Health check endpoint
- `/ready` - Readiness check endpoint

Prometheus is configured to scrape these endpoints at specified intervals.

### Implementation Steps

1. **Clone both repositories**:
   ```bash
   git clone https://github.com/Hotoro-Cloud/hotlabel-qa.git
   git clone https://github.com/Hotoro-Cloud/hotlabel-infra.git
   ```

2. **Configure environment variables**:
   Use the `.env` file in the QA service repository with the proper connection parameters:
   ```bash
   cd hotlabel-qa
   ./scripts/setup-env.sh
   ```

3. **Integration testing options**:

   **Option A: Deploy with complete infrastructure**:
   ```bash
   cd hotlabel-infra
   docker-compose -f docker-compose-dev.yml up -d
   ```

   **Option B: Deploy QA service separately**:
   ```bash
   cd hotlabel-qa
   docker-compose -f docker-compose.infra.yml up -d
   ```

4. **Verify integration**:
   ```bash
   # Check if service is healthy
   curl http://localhost:8000/api/v1/quality/health
   
   # Check detailed readiness
   curl http://localhost:8000/api/v1/quality/ready
   
   # Check if service is visible in Prometheus
   curl http://localhost:9090/api/v1/targets | grep qa
   ```

## Task Management Service Integration

Similar to the QA service, the Task Management service connects to its own database and Redis instance:

| Resource | Connection Parameters |
| --- | --- |
| PostgreSQL | `postgresql://postgres:postgres@postgres:5432/hotlabel_tasks` |
| Redis | `redis://redis:6379/1` |

See the task management service repository for specific integration details.

## User Profiling Service Integration

The User Profiling service connects to these resources:

| Resource | Connection Parameters |
| --- | --- |
| PostgreSQL | `postgresql://postgres:postgres@postgres:5432/hotlabel_users` |
| Redis | `redis://redis:6379/3` |

See the user profiling service repository for specific integration details.

## Publisher Management Service Integration

The Publisher Management service connects to these resources:

| Resource | Connection Parameters |
| --- | --- |
| PostgreSQL | `postgresql://postgres:postgres@postgres:5432/hotlabel_publishers` |
| Redis | `redis://redis:6379/0` |

See the publisher management service repository for specific integration details.

## Troubleshooting

### Database Connection Issues

If a service cannot connect to the database:

1. Ensure PostgreSQL is running in the infrastructure:
   ```bash
   docker ps | grep postgres
   ```

2. Verify the database exists:
   ```bash
   docker exec -it hotlabel-postgres psql -U postgres -c "\l"
   ```

3. Check the database connection string in the service's `.env` file.

### Redis Connection Issues

If a service cannot connect to Redis:

1. Ensure Redis is running in the infrastructure:
   ```bash
   docker ps | grep redis
   ```

2. Test Redis connectivity:
   ```bash
   docker exec -it hotlabel-redis redis-cli ping
   ```

3. Verify the Redis database number (0-3) matches the expected configuration for the service.

### Network Issues

If services cannot communicate with each other:

1. Ensure all services are using the same network:
   ```bash
   docker network inspect hotlabel-network
   ```

2. Check service logs for connection errors:
   ```bash
   docker logs hotlabel-qa
   ```

3. Verify service names and ports are correctly referenced in the configuration.

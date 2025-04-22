# HotLabel Infrastructure

This repository contains the infrastructure setup for the HotLabel platform - a crowdsourced data labeling solution that replaces intrusive online advertising with micro data-labeling tasks.

## Architecture

HotLabel consists of four microservices:

1. **Publisher Management** - Handles publisher registration, configuration, and integration with client websites
2. **Task Management** - Manages the creation, distribution, and tracking of labeling tasks
3. **Quality Assurance** - Validates and verifies the quality of submitted task results
4. **User Profiling** - Manages user sessions and builds expertise profiles to match users with appropriate tasks

All services are deployed to a single GCP Compute E2 instance with the following infrastructure:

- **Kong API Gateway** - Routes requests to appropriate services
- **PostgreSQL** - Persistent storage for all services
- **Redis** - In-memory cache and message broker
- **Prometheus & Grafana** - Monitoring and observability

## Microservices Details

### Quality Assurance Service

The Quality Assurance (QA) service is responsible for ensuring data label quality through:

- **Multi-layered validation** with golden set comparison, consensus verification, and statistical analysis
- **Confidence scoring** to route submissions to appropriate validation paths
- **Comprehensive metrics** for monitoring quality

Service configuration:
- Database: PostgreSQL on `postgres:5432/hotlabel_qa`
- Redis: Instance on `redis:6379` using database #2
- Environment variables specified in `docker-compose-dev.yml`
- Health/readiness endpoints monitored by Prometheus
- API endpoints accessible via Kong at `/api/v1/quality/*`

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Setup

1. Clone this repository:
   ```
   git clone https://github.com/Hotoro-Cloud/hotlabel-infra.git
   cd hotlabel-infra
   ```

2. Start the infrastructure:
   ```
   docker-compose -f docker-compose-dev.yml up -d
   ```

3. Access the services:
   - API Gateway: http://localhost:8000
   - Grafana: http://localhost:3000
   - Prometheus: http://localhost:9090
   - QA Service (via Gateway): http://localhost:8000/api/v1/quality/

### Verifying Service Health

To check if all services are running properly:

```bash
# Check QA service health
curl http://localhost:8000/api/v1/quality/health

# Check QA service readiness (DB & Redis connections)
curl http://localhost:8000/api/v1/quality/ready
```

## Development

### Directory Structure

- `docker-compose-dev.yml` - Main Docker Compose configuration for development
- `docker-compose-local.yml` - Simplified setup for local testing
- `kong/` - Kong API Gateway configuration
- `prometheus/` - Prometheus configuration and monitoring setup
- `grafana/` - Grafana dashboards and configuration
- `scripts/` - Utility scripts for deployment and maintenance

### Service Development

Each service can be developed independently or as part of the complete infrastructure:

- For independent development, use the service-specific docker-compose files
- For integrated development, use the infrastructure's docker-compose-dev.yml
- See the [service integration guide](docs/service-integration.md) for details

## Deployment

See the [deployment guide](docs/deployment.md) for instructions on deploying to GCP Compute Engine.

## License

Copyright © 2025 HotLabel
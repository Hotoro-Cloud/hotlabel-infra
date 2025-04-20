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
   docker-compose up -d
   ```

3. Access the services:
   - API Gateway: http://localhost:8000
   - Grafana: http://localhost:3000
   - Prometheus: http://localhost:9090

## Development

### Directory Structure

- `docker-compose.yml` - Main Docker Compose configuration
- `kong/` - Kong API Gateway configuration
- `prometheus/` - Prometheus configuration
- `grafana/` - Grafana dashboards and configuration
- `scripts/` - Utility scripts for deployment and maintenance

## Deployment

See the [deployment guide](docs/deployment.md) for instructions on deploying to GCP Compute Engine.

## License

Copyright © 2025 HotLabel

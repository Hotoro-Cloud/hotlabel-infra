#!/bin/bash

# HotLabel Local Development Setup Script
# This script sets up the local development environment for HotLabel

set -e

echo "Setting up HotLabel local development environment..."

# Check for required tools
echo "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "Error: Git is not installed. Please install Git first."
    exit 1
fi

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please review and update the .env file with your configuration."
fi

# Check if services are already running
if docker ps | grep -q "hotlabel-"; then
    echo "Some HotLabel services are already running. Stopping them..."
    docker-compose down
fi

# Pull latest images
echo "Pulling latest Docker images..."
docker-compose pull

# Build local images
echo "Building local service images..."
docker-compose build

# Start the infrastructure
echo "Starting HotLabel infrastructure..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Check service health
echo "Checking service health..."
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "Warning: API Gateway is not responding. Check logs with 'docker-compose logs kong'"
else
    echo "API Gateway is running."
fi

if ! curl -s http://localhost:9090/-/healthy > /dev/null; then
    echo "Warning: Prometheus is not responding. Check logs with 'docker-compose logs prometheus'"
else
    echo "Prometheus is running."
fi

# Show service URLs
echo ""
echo "HotLabel services are now running!"
echo ""
echo "Service URLs:"
echo "API Gateway:  http://localhost:8000"
echo "Kong Admin:   http://localhost:8001"
echo "Grafana:      http://localhost:3000 (admin/admin)"
echo "Prometheus:   http://localhost:9090"
echo ""
echo "Database (PostgreSQL): localhost:5432"
echo "Redis: localhost:6379"
echo ""
echo "To stop the services, run: docker-compose down"
echo "To view logs, run: docker-compose logs -f [service_name]"
echo ""
echo "Happy coding!"

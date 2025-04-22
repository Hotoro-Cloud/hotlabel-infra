#!/bin/bash

# HotLabel Complete Deployment Script
# This script deploys both the infrastructure and all microservices for HotLabel

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Log function for better output
log() {
  local level=$1
  local message=$2
  local color=""
  
  case $level in
    "INFO") color=$GREEN ;;
    "WARN") color=$YELLOW ;;
    "ERROR") color=$RED ;;
    *) color=$NC ;;
  esac
  
  echo -e "${color}[$level] $message${NC}"
}

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
  log "ERROR" "Docker is not installed. Please install Docker first."
  exit 1
fi

if ! command -v docker-compose &> /dev/null; then
  log "ERROR" "Docker Compose is not installed. Please install Docker Compose first."
  exit 1
fi

# Create directory structure
DEPLOY_DIR="${HOME}/hotlabel-deployment"
INFRA_DIR="${DEPLOY_DIR}/hotlabel-infra"
TASKS_DIR="${DEPLOY_DIR}/hotlabel-tasks"
PUBLISHERS_DIR="${DEPLOY_DIR}/hotlabel-publishers"
QA_DIR="${DEPLOY_DIR}/hotlabel-qa"
USERS_DIR="${DEPLOY_DIR}/hotlabel-users"

mkdir -p $DEPLOY_DIR

log "INFO" "Starting HotLabel deployment in ${DEPLOY_DIR}"

# Clone or update the repositories
if [ -d "$INFRA_DIR" ]; then
  log "INFO" "Updating hotlabel-infra repository..."
  cd $INFRA_DIR
  git pull
else
  log "INFO" "Cloning hotlabel-infra repository..."
  git clone https://github.com/Hotoro-Cloud/hotlabel-infra.git $INFRA_DIR
  cd $INFRA_DIR
fi

# Clone or update the microservice repositories
for repo in "hotlabel-tasks" "hotlabel-publishers" "hotlabel-qa" "hotlabel-users"; do
  local repo_dir="${DEPLOY_DIR}/${repo}"
  if [ -d "$repo_dir" ]; then
    log "INFO" "Updating ${repo} repository..."
    cd $repo_dir
    git pull
  else
    log "INFO" "Cloning ${repo} repository..."
    git clone https://github.com/Hotoro-Cloud/${repo}.git $repo_dir
  fi
done

# Create .env files for each service
log "INFO" "Creating/updating environment files..."

# Infrastructure .env
if [ ! -f "${INFRA_DIR}/.env" ]; then
  cp "${INFRA_DIR}/.env.example" "${INFRA_DIR}/.env"
  log "INFO" "Created .env file for infrastructure"
fi

# Tasks service .env
if [ ! -f "${TASKS_DIR}/.env" ]; then
  cp "${TASKS_DIR}/.env.example" "${TASKS_DIR}/.env"
  log "INFO" "Created .env file for tasks service"
fi

# Start infrastructure first
log "INFO" "Starting infrastructure services..."
cd $INFRA_DIR
docker-compose -f docker-compose-dev.yml up -d

# Wait for infrastructure to be ready
log "INFO" "Waiting for infrastructure to be ready..."
sleep 15

# Create the network if it doesn't exist
if ! docker network inspect hotlabel-network &> /dev/null; then
  log "INFO" "Creating Docker network hotlabel-network..."
  docker network create hotlabel-network
fi

# Start the microservices
log "INFO" "Starting tasks service..."
cd $TASKS_DIR
docker-compose up -d

# Verify the deployment
log "INFO" "Verifying deployment..."
if docker ps | grep -q "hotlabel-kong"; then
  log "INFO" "Infrastructure is running"
else
  log "ERROR" "Infrastructure failed to start"
  exit 1
fi

if docker ps | grep -q "hotlabel-tasks-api"; then
  log "INFO" "Tasks service is running"
else
  log "ERROR" "Tasks service failed to start"
  exit 1
fi

# Print access information
API_URL="http://localhost:8000/api/v1"
GRAFANA_URL="http://localhost:3000"

log "INFO" "Deployment completed successfully!"
log "INFO" "API Gateway: ${API_URL}"
log "INFO" "Grafana Dashboard: ${GRAFANA_URL} (admin/admin)"
log "INFO" "To test the tasks service, you can access: ${API_URL}/tasks/health"

exit 0

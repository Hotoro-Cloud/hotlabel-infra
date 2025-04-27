#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Base URL for Kong API Gateway
KONG_URL="http://localhost:8000"

# Function to test an endpoint
test_endpoint() {
  local service=$1
  local endpoint=$2
  local expected_status=$3
  
  echo -e "${YELLOW}Testing ${service} ${endpoint}...${NC}"
  
  response=$(curl -s -w "%{http_code}" -o /dev/null "${KONG_URL}${endpoint}")
  
  if [ "$response" -eq "$expected_status" ]; then
    echo -e "${GREEN}✓ Success: ${service} ${endpoint} returned ${response}${NC}"
    return 0
  else
    echo -e "${RED}✗ Failed: ${service} ${endpoint} returned ${response}, expected ${expected_status}${NC}"
    return 1
  fi
}

# Function to test health endpoints
test_health() {
  local service=$1
  local prefix=$2
  
  test_endpoint "$service" "${prefix}/health" 200
  test_endpoint "$service" "${prefix}/ready" 200
}

# Function to test documentation endpoints
test_docs() {
  local service=$1
  local prefix=$2
  
  test_endpoint "$service" "${prefix}/docs" 200
  test_endpoint "$service" "${prefix}/redoc" 200
  test_endpoint "$service" "${prefix}/openapi.json" 200
}

# Test all services
echo "Testing API endpoints through Kong API Gateway..."
echo "================================================="

# Test Publishers Service
echo -e "\n${YELLOW}Testing Publishers Service${NC}"
test_health "Publishers" "/api/v1/publishers"
test_docs "Publishers" "/api/v1/publishers"

# Test Tasks Service
echo -e "\n${YELLOW}Testing Tasks Service${NC}"
test_health "Tasks" "/api/v1/tasks"
test_docs "Tasks" "/api/v1/tasks"

# Test QA Service
echo -e "\n${YELLOW}Testing QA Service${NC}"
test_health "QA" "/api/v1/quality"
test_docs "QA" "/api/v1/quality"

# Test Users Service
echo -e "\n${YELLOW}Testing Users Service${NC}"
test_health "Users" "/api/v1/users"
test_docs "Users" "/api/v1/users"

echo -e "\n${YELLOW}API endpoint testing complete!${NC}" 
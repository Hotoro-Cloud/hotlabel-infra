#!/bin/bash

# Base URL for Kong API Gateway
KONG_URL="http://localhost:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Function to test an endpoint
test_endpoint() {
    local service=$1
    local endpoint=$2
    local method=${3:-GET}
    
    echo -n "Testing $method $service$endpoint... "
    response=$(curl -s -o /dev/null -w "%{http_code}" -X $method "$KONG_URL$service$endpoint")
    
    if [ "$response" -ge 200 ] && [ "$response" -lt 500 ]; then
        echo -e "${GREEN}OK${NC} (HTTP $response)"
    else
        echo -e "${RED}FAILED${NC} (HTTP $response)"
    fi
}

echo "Testing Publishers Service endpoints..."
test_endpoint "/api/v1/publishers" ""
test_endpoint "/api/v1/publishers" "/health"
test_endpoint "/api/v1/publishers" "/docs"
test_endpoint "/api/v1/publishers" "/openapi.json"

echo -e "\nTesting Tasks Service endpoints..."
test_endpoint "/api/v1/tasks" ""
test_endpoint "/api/v1/tasks" "/health"
test_endpoint "/api/v1/tasks" "/docs"
test_endpoint "/api/v1/tasks" "/openapi.json"
test_endpoint "/api/v1/datasets" ""

echo -e "\nTesting QA Service endpoints..."
test_endpoint "/api/v1/qa" ""
test_endpoint "/api/v1/qa" "/health"
test_endpoint "/api/v1/qa" "/docs"
test_endpoint "/api/v1/qa" "/openapi.json"

echo -e "\nTesting Users Service endpoints..."
test_endpoint "/api/v1/users" ""
test_endpoint "/api/v1/users" "/health"
test_endpoint "/api/v1/users" "/docs"
test_endpoint "/api/v1/users" "/openapi.json"
test_endpoint "/api/v1/users" "/search" 
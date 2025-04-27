# HotLabel API Endpoints

This document provides information about the API endpoints available through the Kong API Gateway for the HotLabel platform.

## Base URL

All API endpoints are accessible through the Kong API Gateway at:

```
http://localhost:8000
```

## Service Endpoints

### Users Service (`/api/v1/users`)

#### User Management
- `POST /users` - Create a new user
- `GET /users/{user_id}` - Get user details
- `PUT /users/{user_id}` - Update user details
- `DELETE /users/{user_id}` - Delete a user
- `GET /users` - List all users

#### User Profiles
- `POST /profiles` - Create a user profile
- `GET /profiles/{profile_id}` - Get profile details
- `PUT /profiles/{profile_id}` - Update profile
- `DELETE /profiles/{profile_id}` - Delete a profile
- `GET /profiles` - List all profiles

#### User Expertise
- `POST /expertise` - Add user expertise
- `GET /expertise/{expertise_id}` - Get expertise details
- `PUT /expertise/{expertise_id}` - Update expertise
- `DELETE /expertise/{expertise_id}` - Delete expertise
- `GET /expertise` - List all expertise entries

#### User Sessions
- `POST /sessions` - Create a new session
- `GET /sessions/{session_id}` - Get session details
- `PUT /sessions/{session_id}` - Update session
- `DELETE /sessions/{session_id}` - Delete a session
- `GET /sessions` - List all sessions

#### User Statistics
- `GET /statistics/users/{user_id}` - Get user statistics
- `GET /statistics/profiles/{profile_id}` - Get profile statistics
- `GET /statistics/expertise/{expertise_id}` - Get expertise statistics
- `GET /statistics/sessions/{session_id}` - Get session statistics

### Tasks Service (`/api/v1/tasks`)

#### Dataset Management
- `POST /datasets` - Create a new dataset
- `GET /datasets/{dataset_id}` - Get dataset details
- `PUT /datasets/{dataset_id}` - Update dataset
- `DELETE /datasets/{dataset_id}` - Delete a dataset
- `GET /datasets` - List all datasets

### Quality Assurance Service (`/api/v1/quality`)

#### Validation
- `POST /validation/tasks` - Validate task annotations
- `GET /validation/tasks/{task_id}` - Get task validation results
- `PUT /validation/tasks/{task_id}` - Update task validation
- `GET /validation/tasks` - List all task validations

#### Consensus
- `POST /consensus/tasks` - Create consensus task
- `GET /consensus/tasks/{task_id}` - Get consensus results
- `PUT /consensus/tasks/{task_id}` - Update consensus task
- `GET /consensus/tasks` - List all consensus tasks

#### Metrics
- `GET /metrics/tasks/{task_id}` - Get task metrics
- `GET /metrics/validators/{validator_id}` - Get validator metrics
- `GET /metrics/consensus/{consensus_id}` - Get consensus metrics
- `GET /metrics` - Get overall QA metrics

#### Reports
- `GET /reports/tasks` - Generate task reports
- `GET /reports/validators` - Generate validator reports
- `GET /reports/consensus` - Generate consensus reports
- `GET /reports` - Generate overall QA reports

#### Admin
- `POST /admin/validators` - Add a validator
- `GET /admin/validators/{validator_id}` - Get validator details
- `PUT /admin/validators/{validator_id}` - Update validator
- `DELETE /admin/validators/{validator_id}` - Remove a validator
- `GET /admin/validators` - List all validators

### Common Endpoints for All Services

Each service also provides the following common endpoints:

- **API Documentation**: `/{service}/docs`
- **ReDoc Documentation**: `/{service}/redoc`
- **OpenAPI Schema**: `/{service}/openapi.json`
- **Health Check**: `/{service}/health`
- **Ready Check**: `/{service}/ready`

## Testing API Endpoints

You can test all API endpoints using the provided script:

```bash
cd /path/to/hotlabel-infra
./scripts/test-api-endpoints.sh
```

## API Response Format

All API responses follow a consistent format:

### Success Response

```json
{
  "data": {
    // Response data
  }
}
```

### Error Response

```json
{
  "error": {
    "code": "error_code",
    "message": "Error message",
    "details": {
      // Additional error details
    },
    "request_id": "uuid"
  }
}
```

## Request ID Tracking

All requests through the Kong API Gateway include a `X-Request-ID` header, which is used for request tracking and correlation. This ID is included in error responses and can be used for troubleshooting.

## Rate Limiting

The Kong API Gateway applies rate limiting to all endpoints. The default limit is 100 requests per minute per IP address.

## CORS

CORS is enabled for all endpoints, allowing cross-origin requests from any origin. In production, this should be restricted to specific origins.

## Authentication

Authentication is not currently implemented but can be added using Kong plugins such as JWT or OAuth2. 
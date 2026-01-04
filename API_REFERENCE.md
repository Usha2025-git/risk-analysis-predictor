# API Reference

## Base URL

```
Development: http://localhost:8000/api/v1
Production: https://your-domain.com/api/v1
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Authentication Endpoints

### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "secure_password_123"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "john_doe",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password_123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "john_doe",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  }
}
```

### Get Current User
```http
GET /auth/me
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "john_doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

## Projects Endpoints

### List Projects
```http
GET /projects?skip=0&limit=100&status=active
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (integer, default: 0) - Number of records to skip
- `limit` (integer, default: 100) - Number of records to return
- `status` (string, optional) - Filter by status (planning, active, on_hold, completed, cancelled)

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "name": "Project Alpha",
    "description": "Detailed description",
    "status": "active",
    "start_date": "2024-01-01",
    "planned_end_date": "2024-06-01",
    "actual_end_date": null,
    "team_size": 5,
    "manager": "John Doe",
    "budget": 100000,
    "actual_cost": 45000,
    "risk_level": "medium",
    "health_score": 0.85,
    "success_probability": 0.92,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-15T00:00:00"
  }
]
```

### Create Project
```http
POST /projects
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Project Beta",
  "description": "Project description",
  "start_date": "2024-02-01",
  "planned_end_date": "2024-07-01",
  "team_size": 8,
  "manager": "Jane Smith",
  "budget": 150000,
  "risk_level": "high"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "name": "Project Beta",
  "description": "Project description",
  "status": "planning",
  "start_date": "2024-02-01",
  "planned_end_date": "2024-07-01",
  "actual_end_date": null,
  "team_size": 8,
  "manager": "Jane Smith",
  "budget": 150000,
  "actual_cost": 0,
  "risk_level": "high",
  "health_score": 0.7,
  "success_probability": 0.8,
  "created_at": "2024-02-01T00:00:00",
  "updated_at": "2024-02-01T00:00:00"
}
```

### Get Project Details
```http
GET /projects/{project_id}
Authorization: Bearer <access_token>
```

**Response (200 OK):** Same as above

### Update Project
```http
PUT /projects/{project_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "active",
  "health_score": 0.88,
  "success_probability": 0.95
}
```

**Response (200 OK):** Updated project object

### Delete Project
```http
DELETE /projects/{project_id}
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "detail": "Project deleted successfully"
}
```

### Analyze Project
```http
POST /projects/{project_id}/analyze
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "project_id": "uuid",
  "risks": [
    {
      "id": "uuid",
      "title": "Resource Constraint",
      "severity": "high",
      "probability": 0.8,
      "impact": 0.7,
      "risk_score": 56.0
    }
  ],
  "resources": {
    "available": 5,
    "allocated": 4,
    "utilization": 0.8
  },
  "bottlenecks": [
    "Resource shortage",
    "Schedule pressure"
  ],
  "recommendations": [
    "Hire additional resources",
    "Review timeline",
    "Implement risk mitigation"
  ],
  "overall_risk_score": 45.5,
  "success_probability": 0.82
}
```

## Risks Endpoints

### List Risks
```http
GET /risks?skip=0&limit=100&project_id=uuid&severity=high
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (integer, default: 0)
- `limit` (integer, default: 100)
- `project_id` (string, optional) - Filter by project
- `severity` (string, optional) - Filter by severity (low, medium, high, critical)

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "project_id": "uuid",
    "title": "Budget Overrun",
    "description": "Risk of exceeding budget",
    "category": "financial",
    "severity": "high",
    "probability": 0.6,
    "impact": 0.8,
    "risk_score": 48.0,
    "status": "identified",
    "mitigation_strategy": "Implement cost controls",
    "mitigation_owner": "Finance Team",
    "mitigation_deadline": "2024-02-15",
    "incident_frequency": 2,
    "created_at": "2024-01-20T00:00:00",
    "updated_at": "2024-01-20T00:00:00"
  }
]
```

### Create Risk
```http
POST /risks
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "project_id": "uuid",
  "title": "Technical Challenge",
  "description": "Integration complexity",
  "category": "technical",
  "severity": "medium",
  "probability": 0.5,
  "impact": 0.6
}
```

**Response (201 Created):**
Risk object with calculated `risk_score = probability × impact × 100`

### Get Risk Details
```http
GET /risks/{risk_id}
Authorization: Bearer <access_token>
```

### Update Risk
```http
PUT /risks/{risk_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "mitigating",
  "mitigation_strategy": "Updated strategy",
  "probability": 0.3
}
```

**Note:** Risk score is recalculated if probability or impact changes

### Delete Risk
```http
DELETE /risks/{risk_id}
Authorization: Bearer <access_token>
```

## Resources Endpoints

### List Resources
```http
GET /resources?skip=0&limit=100&skill_category=backend&status=available
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (integer, default: 0)
- `limit` (integer, default: 100)
- `skill_category` (string, optional)
- `status` (string, optional) - available, on_leave, unavailable

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "name": "Alice Johnson",
    "email": "alice@example.com",
    "skill_category": "backend",
    "skill_level": "senior",
    "current_allocation": 0.8,
    "max_allocation": 1.0,
    "hourly_rate": 75,
    "status": "available",
    "availability_start": "2024-01-01",
    "availability_end": null,
    "productivity_score": 0.92,
    "quality_score": 0.88,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-20T00:00:00"
  }
]
```

### Create Resource
```http
POST /resources
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Bob Wilson",
  "email": "bob@example.com",
  "skill_category": "frontend",
  "skill_level": "mid",
  "max_allocation": 1.0,
  "hourly_rate": 60,
  "status": "available"
}
```

### Get Resource Details
```http
GET /resources/{resource_id}
Authorization: Bearer <access_token>
```

### Update Resource
```http
PUT /resources/{resource_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_allocation": 0.7,
  "productivity_score": 0.95
}
```

### Delete Resource
```http
DELETE /resources/{resource_id}
Authorization: Bearer <access_token>
```

### Allocate Resource
```http
POST /resources/{resource_id}/allocate
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "allocation": 0.9
}
```

**Response (200 OK):**
```json
{
  "resource_id": "uuid",
  "current_allocation": 0.9,
  "max_allocation": 1.0
}
```

## Analytics Endpoints

### Dashboard Statistics
```http
GET /analytics/dashboard
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "total_projects": 25,
  "active_projects": 8,
  "completed_projects": 12,
  "average_health_score": 0.78,
  "average_success_probability": 0.85,
  "high_risk_projects": 3,
  "critical_risks": 5,
  "total_resources": 15,
  "average_resource_utilization": 72.5,
  "overall_risk_score": 38.2
}
```

### Trends
```http
GET /analytics/trends?days=30
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `days` (integer, default: 30) - Look-back period

**Response (200 OK):**
```json
{
  "time_period": "Last 30 days",
  "projects_created": 5,
  "projects_completed": 3,
  "success_rate": 60.0,
  "risks_identified": 12,
  "high_severity_risks": 4,
  "average_risk_score": 42.5,
  "total_data_points": 17,
  "recommendations": [
    "Monitor high-severity risks",
    "Allocate resources strategically",
    "Review completed projects"
  ]
}
```

### Success Rate Prediction
```http
GET /analytics/predictions/success-rate?project_id=uuid
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `project_id` (string, optional) - Specific project or all projects

**Response (200 OK):**
```json
{
  "project_id": "uuid",
  "predicted_success_rate": 85.5,
  "confidence_level": "high",
  "risk_factors": [
    "Resource constraints",
    "Schedule risks",
    "Technical complexity"
  ],
  "recommendations": [
    "Increase team size",
    "Add buffer to schedule",
    "Implement risk mitigation"
  ]
}
```

### Identify Bottlenecks
```http
GET /analytics/bottlenecks
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "bottleneck_count": 3,
  "bottlenecks": [
    {
      "type": "Over-allocation",
      "resource_id": "uuid",
      "resource_name": "Alice Johnson",
      "current": 1.2,
      "max": 1.0,
      "severity": "high"
    },
    {
      "type": "Resource shortage",
      "project_id": "uuid",
      "project_name": "Project Alpha",
      "required": 5,
      "assigned": 3,
      "severity": "high"
    }
  ],
  "critical_count": 2,
  "recommendations": [
    "Review allocation strategy",
    "Redistribute workload",
    "Hire additional resources"
  ]
}
```

## WebSocket

### Connect
```
WS ws://localhost:8000/api/v1/ws/{client_id}
```

### Subscribe to Events
```json
{
  "type": "subscribe",
  "event_type": "project_created",
  "client_id": "unique-id"
}
```

### Unsubscribe
```json
{
  "type": "unsubscribe",
  "event_type": "project_created",
  "client_id": "unique-id"
}
```

### Receive Messages
```json
{
  "type": "message",
  "event_type": "project_created",
  "data": {
    "id": "uuid",
    "name": "New Project",
    ...
  }
}
```

**Event Types:**
- `project_created`
- `project_updated`
- `risk_identified`
- `resource_allocated`
- `analytics_update`

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

Currently not implemented but recommended for production:
- 100 requests per minute per IP
- 1000 requests per hour per user

## CORS

Allowed origins (configurable via `CORS_ORIGINS` in `.env`):
- http://localhost:5173
- http://localhost:3000
- http://frontend

---

**Last Updated:** January 2024  
**API Version:** 1.0.0

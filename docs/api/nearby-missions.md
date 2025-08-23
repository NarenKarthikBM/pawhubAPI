# Nearby Missions API Documentation

## Overview

The Nearby Missions API allows authenticated users to discover upcoming and ongoing organisation missions (like vaccination drives, adoption drives, rescue missions, etc.) within a 20km radius of their location.

## Endpoint

```
GET /api/organisations/missions/nearby/
```

## Authentication

**Required**: User Token Authentication

Include the authentication token in the request header:

```
Authorization: Token your_user_token_here
```

## Query Parameters

| Parameter      | Type   | Required | Description                                                                                |
| -------------- | ------ | -------- | ------------------------------------------------------------------------------------------ |
| `latitude`     | Number | Yes      | Latitude coordinate                                                                        |
| `longitude`    | Number | Yes      | Longitude coordinate                                                                       |
| `mission_type` | String | No       | Filter by mission type (vaccination, adoption, rescue, awareness, feeding, medical, other) |

## Response

### Success Response (200 OK)

Returns an array of mission objects:

```json
[
  {
    "id": 1,
    "title": "Free Pet Vaccination Drive",
    "description": "Free vaccination for all pets in the area",
    "mission_type": "vaccination",
    "mission_type_display": "Vaccination Drive",
    "city": "San Francisco",
    "area": "Mission District",
    "location": {
      "latitude": 37.7749,
      "longitude": -122.4194
    },
    "start_datetime": "2025-08-25T10:00:00Z",
    "end_datetime": "2025-08-25T16:00:00Z",
    "is_active": true,
    "max_participants": 100,
    "contact_phone": "+1-555-0123",
    "contact_email": "contact@organization.com",
    "organisation": {
      "id": 1,
      "name": "Pet Care Foundation",
      "email": "info@petcare.org",
      "is_verified": true
    },
    "created_at": "2025-08-20T09:00:00Z",
    "updated_at": "2025-08-20T09:00:00Z"
  }
]
```

### Error Responses

#### 400 Bad Request

```json
{
  "error": "Both latitude and longitude are required and must be valid numbers"
}
```

#### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

## Usage Examples

### Basic Request

```bash
curl -X GET \
  "http://localhost:8000/api/organisations/missions/nearby/?latitude=37.7749&longitude=-122.4194" \
  -H "Authorization: Token your_user_token_here"
```

### With Mission Type Filter

```bash
curl -X GET \
  "http://localhost:8000/api/organisations/missions/nearby/?latitude=37.7749&longitude=-122.4194&mission_type=vaccination" \
  -H "Authorization: Token your_user_token_here"
```

### JavaScript Example

```javascript
const response = await fetch("/api/organisations/missions/nearby/?latitude=37.7749&longitude=-122.4194", {
  method: "GET",
  headers: {
    Authorization: "Token your_user_token_here",
    "Content-Type": "application/json",
  },
});

const missions = await response.json();
console.log(missions);
```

## Features

### Geographic Filtering

- Returns missions within 20km radius of provided coordinates
- Uses PostGIS distance calculations for accurate geographic queries
- Only includes missions with valid location data

### Time Filtering

- Shows only upcoming and ongoing missions (end_datetime >= current time)
- Excludes past missions automatically
- Orders results by start_datetime (earliest first)

### Mission Types

- `vaccination`: Vaccination Drive
- `adoption`: Adoption Drive
- `rescue`: Rescue Mission
- `awareness`: Awareness Campaign
- `feeding`: Feeding Program
- `medical`: Medical Camp
- `other`: Other

### Organisation Details

Each mission includes complete organisation information:

- Organisation name and contact details
- Verification status
- Email address

## Implementation Details

### Performance Optimizations

- Uses database indexes on location fields for fast geographic queries
- Select_related used to minimize database queries
- Indexes on mission_type, start_datetime, end_datetime, and is_active fields

### Security

- Requires user authentication
- Validates coordinate inputs
- Rate limiting through Django REST Framework

### Error Handling

- Validates numeric coordinates
- Handles missing parameters gracefully
- Returns appropriate HTTP status codes

## Related Endpoints

- `GET /api/animals/sightings/nearby/` - Similar endpoint for animal sightings
- `GET /api/animals/emergencies/nearby/` - Similar endpoint for animal emergencies
- `POST /api/users/obtain-auth-token/` - User authentication endpoint

# Organisation Missions List API

## Overview

This API endpoint allows organisations to retrieve a list of their own missions with filtering and pagination capabilities.

## Endpoint

```
GET /api/organisations/missions/
```

## Authentication

This endpoint requires organisation authentication using:

- `Authorization` header with organisation auth token
- `Device-Token` header with organisation device token

## Query Parameters

| Parameter      | Type    | Required | Description                                                                                             |
| -------------- | ------- | -------- | ------------------------------------------------------------------------------------------------------- |
| `status`       | string  | No       | Filter by mission status: `upcoming`, `ongoing`, `completed`, or `all` (default: `all`)                 |
| `mission_type` | string  | No       | Filter by mission type: `vaccination`, `adoption`, `rescue`, `awareness`, `feeding`, `medical`, `other` |
| `city`         | string  | No       | Filter by city (case-insensitive partial match)                                                         |
| `limit`        | integer | No       | Number of missions to return (default: 20, max: 100)                                                    |
| `offset`       | integer | No       | Number of missions to skip for pagination (default: 0)                                                  |

## Response Format

### Success Response (200 OK)

```json
{
  "count": 15,
  "missions": [
    {
      "id": 1,
      "title": "Free Pet Vaccination Drive",
      "description": "Free vaccination for all pets in the Mission District area.",
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
      "contact_email": "contact@example.com",
      "created_at": "2025-08-24T12:00:00Z",
      "updated_at": "2025-08-24T12:00:00Z"
    }
  ]
}
```

### Error Responses

#### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 400 Bad Request

```json
{
  "error": "Invalid status filter. Use: upcoming, ongoing, completed, or all"
}
```

## Mission Status Definitions

- **upcoming**: Missions that haven't started yet (`start_datetime > now` and `is_active = true`)
- **ongoing**: Missions currently in progress (`start_datetime <= now <= end_datetime` and `is_active = true`)
- **completed**: Missions that have ended (`end_datetime < now`)
- **all**: All missions regardless of status

## Example Usage

### Get all missions

```bash
curl -X GET "http://localhost:8000/api/organisations/missions/" \
  -H "Authorization: your_auth_token" \
  -H "Device-Token: your_device_token"
```

### Get upcoming vaccination missions

```bash
curl -X GET "http://localhost:8000/api/organisations/missions/?status=upcoming&mission_type=vaccination" \
  -H "Authorization: your_auth_token" \
  -H "Device-Token: your_device_token"
```

### Get missions with pagination

```bash
curl -X GET "http://localhost:8000/api/organisations/missions/?limit=10&offset=20" \
  -H "Authorization: your_auth_token" \
  -H "Device-Token: your_device_token"
```

### Filter by city

```bash
curl -X GET "http://localhost:8000/api/organisations/missions/?city=San Francisco" \
  -H "Authorization: your_auth_token" \
  -H "Device-Token: your_device_token"
```

## Notes

- Missions are ordered by `start_datetime` in descending order (newest first)
- The response excludes organisation details since this endpoint is for the organisation's own missions
- Location coordinates use WGS84 coordinate system (SRID 4326)
- All datetime fields are in ISO 8601 format with UTC timezone
- The `max_participants` field can be null if not specified
- Contact information (`contact_phone`, `contact_email`) can be empty strings if not provided

## Related Models

This API uses the `OrganisationMissions` model with the following key fields:

- Mission details (title, description, type)
- Location information (city, area, coordinates)
- Timing (start/end datetime, active status)
- Contact information
- Participant limits
- Audit fields (created_at, updated_at)

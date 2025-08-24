# Nearby Sightings and Emergencies API for Organizations

## Overview

This API endpoint allows organizations to retrieve both animal sightings and emergencies within a specified radius from given coordinates. Unlike the individual nearby sightings/emergencies endpoints that are limited to 20km, this endpoint accepts a custom radius parameter.

## Endpoint

```
GET /api/organisations/sightings-emergencies/nearby/
```

## Parameters

| Parameter | Type   | Required | Description                                    |
| --------- | ------ | -------- | ---------------------------------------------- |
| latitude  | number | Yes      | Latitude coordinate (decimal degrees)          |
| longitude | number | Yes      | Longitude coordinate (decimal degrees)         |
| radius    | number | Yes      | Search radius in kilometers (must be positive) |

## Example Request

```bash
curl -X GET "http://localhost:8000/api/organisations/sightings-emergencies/nearby/?latitude=40.7128&longitude=-74.0060&radius=50"
```

## Response Format

```json
{
  "sightings": [
    {
      "id": 1,
      "animal": {
        "id": 1,
        "name": "Buddy",
        "species": "Dog",
        "breed": "Golden Retriever",
        "type": "pet"
      },
      "location": {
        "latitude": 40.7128,
        "longitude": -74.006
      },
      "image": {
        "id": 1,
        "image_url": "https://example.com/image.jpg"
      },
      "reporter": {
        "id": 1,
        "username": "john_doe",
        "name": "John Doe"
      },
      "breed_analysis": [],
      "created_at": "2023-08-24T12:00:00Z"
    }
  ],
  "emergencies": [
    {
      "id": 1,
      "emergency_type": "injury",
      "reporter": {
        "id": 2,
        "username": "jane_smith",
        "name": "Jane Smith"
      },
      "location": {
        "latitude": 40.72,
        "longitude": -74.01
      },
      "image": {
        "id": 2,
        "image_url": "https://example.com/emergency.jpg"
      },
      "animal": {
        "id": 2,
        "name": "Max",
        "species": "Cat",
        "breed": "Persian",
        "type": "stray"
      },
      "description": "Injured cat found on the street",
      "status": "active",
      "created_at": "2023-08-24T11:30:00Z"
    }
  ]
}
```

## Features

- **Custom Radius**: Unlike other nearby endpoints, this one accepts any positive radius value (not limited to 20km)
- **Combined Data**: Returns both sightings and emergencies in a single API call
- **Active Only**: Only returns active emergencies (status = "active")
- **Associated Animals Only**: Only returns sightings that have associated animal profiles
- **Optimized Queries**: Uses select_related for efficient database queries

## Error Responses

### 400 Bad Request

```json
{
  "error": "latitude, longitude, and radius are required and must be valid numbers"
}
```

```json
{
  "error": "Radius must be a positive number"
}
```

## Use Cases

1. **Emergency Response**: Organizations can quickly find all nearby incidents requiring attention
2. **Area Monitoring**: Monitor animal activity and emergencies in specific regions
3. **Resource Allocation**: Plan rescue operations based on nearby sightings and emergencies
4. **Custom Coverage Areas**: Use different radius values based on organization capabilities

## Implementation Details

- Built using custom APIView pattern for performance optimization
- Uses GeoDjango's distance queries with PostGIS for accurate geographic calculations
- Implements proper error handling and validation
- Includes comprehensive Swagger documentation
- Follows the project's custom serialization patterns

## Related Endpoints

- `/api/animals/sightings/nearby/` - Individual nearby sightings (20km limit)
- `/api/animals/emergencies/nearby/` - Individual nearby emergencies (20km limit)
- `/api/organisations/missions/nearby/` - Nearby organization missions

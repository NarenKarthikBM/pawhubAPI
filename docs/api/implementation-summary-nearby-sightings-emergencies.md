# Implementation Summary: Nearby Sightings and Emergencies API for Organizations

## Overview

I have successfully created a new API route for organizations that combines animal sightings and emergencies within a custom radius. This API is designed specifically for organizations and does not have the 20km limitation found in the individual nearby sightings/emergencies endpoints.

## What Was Implemented

### 1. New API Endpoint

- **URL**: `/api/organisations/sightings-emergencies/nearby/`
- **Method**: GET
- **Purpose**: Get both animal sightings and emergencies within a specified radius for organizations

### 2. Key Features

#### Custom Radius

- Unlike the existing nearby endpoints that are limited to 20km, this endpoint accepts any positive radius value
- Organizations can search within their operational capabilities (could be 5km, 50km, 100km, etc.)

#### Combined Data

- Returns both sightings and emergencies in a single API call
- Reduces the number of API calls organizations need to make
- Provides a comprehensive view of all incidents in an area

#### Smart Filtering

- **Sightings**: Only includes sightings with associated animal profiles
- **Emergencies**: Only includes active emergencies (status = "active")
- **Performance**: Uses select_related for efficient database queries

#### Comprehensive Error Handling

- Validates all required parameters (latitude, longitude, radius)
- Ensures radius is a positive number
- Returns meaningful error messages for debugging

### 3. API Parameters

| Parameter | Type   | Required | Description                                    |
| --------- | ------ | -------- | ---------------------------------------------- |
| latitude  | number | Yes      | Latitude coordinate (decimal degrees)          |
| longitude | number | Yes      | Longitude coordinate (decimal degrees)         |
| radius    | number | Yes      | Search radius in kilometers (must be positive) |

### 4. Response Structure

```json
{
  "sightings": [
    {
      "id": 1,
      "animal": {
        /* animal profile details */
      },
      "location": { "latitude": 40.7128, "longitude": -74.006 },
      "image": {
        /* image details */
      },
      "reporter": {
        /* user details */
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
        /* user details */
      },
      "location": { "latitude": 40.72, "longitude": -74.01 },
      "image": {
        /* image details */
      },
      "animal": {
        /* animal profile details */
      },
      "description": "Emergency description",
      "status": "active",
      "created_at": "2023-08-24T11:30:00Z"
    }
  ]
}
```

## Files Modified/Created

### 1. Core Implementation

- **`organisations/views.py`**: Added `NearbySightingsAndEmergenciesAPI` class
- **`organisations/urls.py`**: Added URL pattern for the new endpoint

### 2. Documentation

- **`docs/api/nearby-sightings-emergencies-organizations.md`**: Comprehensive API documentation
- **`test_nearby_sightings_emergencies_organizations.py`**: Test script for validation

### 3. Features Added

- Import statements for AnimalSighting, Emergency models and their serializers
- Complete Swagger/OpenAPI documentation
- Comprehensive error handling and validation
- Optimized database queries with select_related

## Technical Implementation Details

### Database Queries

The implementation uses GeoDjango's distance queries with PostGIS for accurate geographic calculations:

```python
# Sightings query
AnimalSighting.objects.filter(
    location__distance_lte=(user_location, D(km=radius)),
    animal__isnull=False,
).select_related("animal", "image", "reporter")

# Emergencies query
Emergency.objects.filter(
    location__distance_lte=(user_location, D(km=radius)),
    status="active",
).select_related("reporter", "image", "animal")
```

### Performance Optimizations

- Uses `select_related()` to avoid N+1 query problems
- Filters out irrelevant data at the database level
- Orders by creation date for chronological relevance

### Error Handling

- Validates parameter types and values
- Provides specific error messages for different failure scenarios
- Returns appropriate HTTP status codes

## Usage Examples

### Basic Request

```bash
curl -X GET "http://localhost:8000/api/organisations/sightings-emergencies/nearby/?latitude=40.7128&longitude=-74.0060&radius=25"
```

### Large Area Search

```bash
curl -X GET "http://localhost:8000/api/organisations/sightings-emergencies/nearby/?latitude=40.7128&longitude=-74.0060&radius=100"
```

## Benefits for Organizations

1. **Operational Flexibility**: Organizations can define their own operational radius
2. **Comprehensive View**: Single API call provides complete incident overview
3. **Resource Planning**: Better allocation of rescue/response resources
4. **Area Monitoring**: Monitor specific regions based on organizational coverage
5. **Emergency Response**: Quick identification of nearby incidents requiring attention

## Integration with Existing System

The new API follows the established patterns in the codebase:

- Uses the same authentication patterns as other organization endpoints
- Follows the custom APIView pattern for performance
- Uses existing serializers and models
- Maintains consistent error handling approaches
- Includes comprehensive Swagger documentation

## Testing

A comprehensive test script has been created (`test_nearby_sightings_emergencies_organizations.py`) that validates:

- Valid requests with different radius values
- Error handling for missing/invalid parameters
- Response structure validation
- Edge cases (negative radius, zero radius, etc.)

The implementation is ready for use and fully integrated with the existing PawHub API system.

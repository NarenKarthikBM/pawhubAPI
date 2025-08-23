# Emergency API Documentation

## Overview

The Emergency API allows users to create emergency reports with location coordinates, descriptions, and optional images. The system supports different emergency types for comprehensive animal care management.

## Emergency Types

The system supports the following emergency types:

1. **`injury`** - For animals that are injured and need medical attention (default)
2. **`rescue_needed`** - For animals that need to be rescued from dangerous situations
3. **`aggressive_behavior`** - For animals displaying aggressive behavior that poses a risk
4. **`missing_lost_pet`** - For pets that are missing or lost (automatically set when using the lost pets API)

## Endpoint

```
POST /api/animals/emergencies/create/
```

## Authentication

- Required: UserTokenAuthentication
- Include authentication token in the request headers

## Request Body

```json
{
  "emergency_type": "injury",
  "longitude": 77.5946,
  "latitude": 12.9716,
  "description": "Injured dog found on the street, needs immediate medical attention",
  "image_url": "https://example.com/emergency-image.jpg"
}
```

### Required Fields

- `longitude` (number): Emergency location longitude coordinate
- `latitude` (number): Emergency location latitude coordinate
- `description` (string): Description of the emergency (minimum 10 characters, maximum 1000 characters)

### Optional Fields

- `emergency_type` (string): Type of emergency. Must be one of: `injury`, `rescue_needed`, `aggressive_behavior`, `missing_lost_pet`. Defaults to `injury` if not specified.
- `image_url` (string): URL of emergency image

## Response

### Success Response (201 Created)

```json
{
  "emergency": {
    "id": 1,
    "emergency_type": "injury",
    "reporter": {
      "id": 1,
      "username": "user123",
      "name": "John Doe"
    },
    "location": {
      "latitude": 12.9716,
      "longitude": 77.5946
    },
    "image": {
      "id": 1,
      "image_url": "https://example.com/emergency-image.jpg"
    },
    "animal": null,
    "description": "Injured dog found on the street, needs immediate medical attention",
    "status": "active",
    "created_at": "2025-08-24T10:30:00Z",
    "updated_at": "2025-08-24T10:30:00Z"
  },
  "message": "Emergency reported successfully"
}
```

### Error Responses

#### 400 Bad Request

```json
{
  "error": "Description should have more than 10 and less than 1000 characters",
  "field": "description"
}
```

#### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

## Implementation Details

### Files Modified/Created

1. **animals/validator.py** - Added `CreateEmergencyInputValidator` class
2. **animals/utils.py** - Added `create_emergency()` utility function
3. **animals/views.py** - Added `EmergencyCreateAPI` class
4. **animals/urls.py** - Added URL pattern for emergency creation

### Database Schema

The Emergency model includes:

- `reporter` (ForeignKey to CustomUser)
- `location` (PointField with WGS84 coordinates)
- `image` (ForeignKey to AnimalMedia, optional)
- `description` (TextField)
- `status` (CharField with choices: 'active', 'resolved')
- `created_at` and `updated_at` (DateTimeFields)

### Validation Rules

- Longitude and latitude must be valid numbers
- Description must be a string with 10-1000 characters
- Image URL is optional but must be a valid string if provided
- User must be authenticated

### Features

- Automatic location point creation from coordinates
- Optional image attachment via AnimalMedia model
- Status automatically set to 'active' for new emergencies
- Comprehensive error handling and validation
- Swagger/OpenAPI documentation integration

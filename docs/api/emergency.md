# Emergency API Documentation

## Overview

The Emergency API allows users to create emergency reports with location coordinates, descriptions, and optional images.

## Endpoint

```
POST /animals/emergencies/
```

## Authentication

- Required: UserTokenAuthentication
- Include authentication token in the request headers

## Request Body

```json
{
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

- `image_url` (string): URL of emergency image

## Response

### Success Response (201 Created)

```json
{
  "emergency": {
    "id": 1,
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

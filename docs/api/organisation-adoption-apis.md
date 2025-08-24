# Organisation Adoption APIs Documentation

This document describes the new APIs for managing adoption listings by organisations.

## Overview

Two new APIs have been added to the PawHub system to allow organisations to:

1. **List their adoption postings** - View all adoption listings they have posted
2. **Mark adoptions as adopted** - Update the status of their adoption listings when pets are adopted

## Authentication

Both APIs require **Organisation Token Authentication**. You need to include the following headers in your requests:

```
Authorization: <organisation_auth_token>
Device-Token: <organisation_device_token>
```

## API Endpoints

### 1. Organisation Adoptions List API

**Endpoint:** `GET /animals/adoptions/my-listings/`

**Description:** Retrieves all adoption listings posted by the authenticated organisation.

**Authentication:** Required (Organisation Token)

**Request Parameters:** None

**Response Format:**

```json
{
  "success": true,
  "adoptions": [
    {
      "id": 1,
      "profile": {
        "id": 5,
        "name": "Buddy",
        "species": "Dog",
        "breed": "Golden Retriever",
        "type": "stray",
        "images": [
          {
            "id": 10,
            "image_url": "https://example.com/buddy.jpg"
          }
        ],
        "location": {
          "latitude": 40.7128,
          "longitude": -74.006
        },
        "is_sterilized": true,
        "breed_analysis": ["friendly", "energetic"],
        "created_at": "2025-08-24T10:30:00Z",
        "updated_at": "2025-08-24T12:00:00Z"
      },
      "posted_by": {
        "id": 3,
        "name": "City Animal Shelter",
        "email": "contact@cityanimalshelter.org",
        "is_verified": true
      },
      "description": "Buddy is a friendly and energetic Golden Retriever looking for a loving home.",
      "status": "available",
      "created_at": "2025-08-24T10:30:00Z",
      "updated_at": "2025-08-24T10:30:00Z"
    }
  ],
  "count": 1,
  "organisation": {
    "id": 3,
    "name": "City Animal Shelter",
    "email": "contact@cityanimalshelter.org",
    "is_verified": true
  }
}
```

**Status Codes:**

- `200` - Success
- `401` - Authentication failed
- `500` - Internal server error

### 2. Mark Adoption as Adopted API

**Endpoint:** `PATCH /animals/adoptions/mark-adopted/`

**Description:** Marks an adoption listing as adopted. Only the organisation that posted the adoption can mark it as adopted.

**Authentication:** Required (Organisation Token)

**Request Body:**

```json
{
  "adoption_id": 1
}
```

**Request Parameters:**

- `adoption_id` (integer, required): ID of the adoption listing to mark as adopted

**Response Format:**

```json
{
  "success": true,
  "message": "Adoption listing marked as adopted successfully",
  "adoption": {
    "id": 1,
    "profile": {
      "id": 5,
      "name": "Buddy",
      "species": "Dog",
      "breed": "Golden Retriever",
      "type": "stray",
      "images": [
        {
          "id": 10,
          "image_url": "https://example.com/buddy.jpg"
        }
      ],
      "location": {
        "latitude": 40.7128,
        "longitude": -74.006
      },
      "is_sterilized": true,
      "breed_analysis": ["friendly", "energetic"],
      "created_at": "2025-08-24T10:30:00Z",
      "updated_at": "2025-08-24T12:00:00Z"
    },
    "posted_by": {
      "id": 3,
      "name": "City Animal Shelter",
      "email": "contact@cityanimalshelter.org",
      "is_verified": true
    },
    "description": "Buddy is a friendly and energetic Golden Retriever looking for a loving home.",
    "status": "adopted",
    "created_at": "2025-08-24T10:30:00Z",
    "updated_at": "2025-08-24T14:30:00Z"
  }
}
```

**Status Codes:**

- `200` - Success
- `400` - Invalid input data
- `401` - Authentication failed
- `404` - Adoption listing not found or no permission to modify
- `500` - Internal server error

**Error Cases:**

- Adoption listing not found
- Organisation doesn't have permission to modify the adoption
- Adoption is already marked as adopted
- Invalid adoption ID

## Usage Examples

### List Organisation Adoptions

```bash
curl -X GET "http://localhost:8000/animals/adoptions/my-listings/" \
     -H "Authorization: your_org_auth_token" \
     -H "Device-Token: your_org_device_token"
```

### Mark Adoption as Adopted

```bash
curl -X PATCH "http://localhost:8000/animals/adoptions/mark-adopted/" \
     -H "Authorization: your_org_auth_token" \
     -H "Device-Token: your_org_device_token" \
     -H "Content-Type: application/json" \
     -d '{"adoption_id": 1}'
```

## Error Handling

All APIs return consistent error responses in the following format:

```json
{
  "error": "Error message describing what went wrong"
}
```

Common error scenarios:

1. **Authentication Failure (401)**: Invalid or missing auth tokens
2. **Permission Denied (404)**: Trying to access/modify adoptions not posted by your organisation
3. **Validation Error (400)**: Invalid or missing required parameters
4. **Already Adopted (500)**: Attempting to mark an already adopted pet as adopted again

## Database Models

The APIs work with the existing `Adoption` model which has the following key fields:

- `id`: Primary key
- `profile`: Foreign key to `AnimalProfileModel`
- `posted_by`: Foreign key to `Organisation`
- `description`: Text description of the adoption
- `status`: Choice field ('available' or 'adopted')
- `created_at`: Timestamp when created
- `updated_at`: Timestamp when last modified

## Security Considerations

1. **Organisation Authentication**: Both APIs require valid organisation tokens
2. **Permission Control**: Organisations can only access/modify their own adoption listings
3. **Input Validation**: All input parameters are validated before processing
4. **Error Handling**: Sensitive information is not exposed in error messages

## Integration Notes

- These APIs integrate with the existing animal profile and organisation systems
- The adoption status changes are automatically timestamped
- The APIs maintain consistency with the existing codebase patterns and serialization methods
- All datetime fields are serialized using the project's standard datetime utility

## Testing

A test script (`test_adoption_apis.py`) is provided to verify the functionality of both APIs. Update the authentication tokens in the script and run it to test the implementation.

## Future Enhancements

Potential future improvements could include:

- Pagination for large lists of adoptions
- Filtering and search capabilities
- Bulk operations for marking multiple adoptions
- Email notifications when adoptions are marked as adopted
- Analytics and reporting for adoption success rates

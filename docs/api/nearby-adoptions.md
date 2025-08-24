# Nearby Adoptions API Implementation

## Overview

This document describes the implementation of the Nearby Adoptions API endpoint that allows users to discover adoption listings from verified organizations within a specified radius of their location.

## Endpoint Details

### URL

```
GET /animals/adoptions/nearby/
```

### Authentication

- Requires user authentication via `UserTokenAuthentication`
- Users must be logged in to access this endpoint

### Parameters

#### Required Parameters

- `latitude` (float): User's latitude coordinate
- `longitude` (float): User's longitude coordinate

#### Optional Parameters

- `radius` (float): Search radius in kilometers
  - Default: 20km
  - Range: 1-100km
  - Values outside this range will return a validation error

### Response Format

#### Success Response (200 OK)

```json
{
  "success": true,
  "adoptions": [
    {
      "id": 1,
      "profile": {
        "id": 1,
        "name": "Buddy",
        "species": "Dog",
        "breed": "Golden Retriever",
        "type": "stray",
        "images": [
          {
            "id": 1,
            "image_url": "https://example.com/image.jpg"
          }
        ],
        "location": {
          "latitude": 40.7128,
          "longitude": -74.006
        },
        "is_sterilized": true,
        "created_at": "2025-08-24T10:30:00Z",
        "updated_at": "2025-08-24T10:30:00Z"
      },
      "posted_by": {
        "id": 1,
        "name": "NYC Animal Shelter",
        "email": "contact@nycanimalshelter.org",
        "is_verified": true,
        "location": {
          "latitude": 40.758,
          "longitude": -73.9855
        },
        "address": "326 E 110th St, New York, NY 10029"
      },
      "description": "Buddy is a friendly and energetic dog looking for a loving home...",
      "status": "available",
      "distance_km": 12.5,
      "created_at": "2025-08-24T10:30:00Z",
      "updated_at": "2025-08-24T10:30:00Z"
    }
  ],
  "count": 1,
  "search_radius_km": 20,
  "user_location": {
    "latitude": 40.7128,
    "longitude": -74.006
  }
}
```

#### Error Responses

##### 400 Bad Request

```json
{
  "error": "Latitude must be a valid number"
}
```

##### 500 Internal Server Error

```json
{
  "error": "Failed to retrieve nearby adoptions: Database connection error"
}
```

## Implementation Details

### Key Features

1. **Geospatial Filtering**: Uses PostGIS to efficiently query organizations within the specified radius
2. **Verified Organizations Only**: Only shows listings from verified organizations (`is_verified=True`)
3. **Available Listings Only**: Filters for adoption listings with `status="available"`
4. **Distance Calculation**: Calculates and returns the distance to each organization
5. **Complete Animal Profiles**: Returns full animal profile details including images
6. **Organization Details**: Includes organization location, address, and verification status
7. **Input Validation**: Comprehensive validation of coordinates and radius parameters
8. **Error Handling**: Robust error handling with descriptive error messages

### Database Queries

The implementation uses Django's GIS capabilities with the following optimizations:

1. **Efficient Spatial Query**: Uses `distance_lte` filter for radius-based filtering
2. **Select Related**: Optimizes database queries with `select_related("profile", "posted_by")`
3. **Prefetch Related**: Loads related images efficiently with `prefetch_related("profile__images")`
4. **Ordering**: Results are ordered by creation date (newest first)

### Validation Logic

The `NearbyAdoptionsInputValidator` class handles:

- **Coordinate Validation**: Ensures latitude and longitude are valid numbers
- **Radius Validation**: Enforces range limits (1-100km)
- **Type Checking**: Validates parameter types and converts as needed

### Utility Function

The `get_nearby_adoptions()` utility function:

1. Creates a PostGIS Point from user coordinates
2. Queries for available adoptions within radius from verified organizations
3. Calculates distances using PostGIS geometry functions
4. Serializes data with enhanced organization details
5. Returns structured response with metadata

## Usage Examples

### Basic Request

```bash
curl -X GET \
  "http://localhost:8000/animals/adoptions/nearby/?latitude=40.7128&longitude=-74.0060" \
  -H "Authorization: Token YOUR_AUTH_TOKEN"
```

### With Custom Radius

```bash
curl -X GET \
  "http://localhost:8000/animals/adoptions/nearby/?latitude=40.7128&longitude=-74.0060&radius=50" \
  -H "Authorization: Token YOUR_AUTH_TOKEN"
```

### JavaScript Example

```javascript
const response = await fetch("/animals/adoptions/nearby/?latitude=40.7128&longitude=-74.0060&radius=30", {
  headers: {
    Authorization: "Token " + userToken,
  },
});

const data = await response.json();
if (data.success) {
  console.log(`Found ${data.count} adoptions within ${data.search_radius_km}km`);
  data.adoptions.forEach((adoption) => {
    console.log(`${adoption.profile.name} at ${adoption.posted_by.name} (${adoption.distance_km}km away)`);
  });
}
```

## Integration Notes

### Frontend Integration

- The API returns all necessary data for displaying adoption cards/listings
- Distance information helps with sorting and filtering on the frontend
- Organization verification status can be displayed as trust indicators
- Image URLs are ready for direct display

### Mobile App Considerations

- The API works well with device GPS coordinates
- Default 20km radius is suitable for most urban areas
- Configurable radius allows users to expand search in rural areas

### Performance Considerations

- PostGIS spatial indexes ensure efficient geospatial queries
- Select/prefetch related optimizations minimize database hits
- Reasonable default radius prevents overly large result sets

## Future Enhancements

Potential improvements and related endpoints:

1. **Adoption Application**: `POST /animals/adoptions/{id}/apply/`
2. **Organization Management**: Endpoints for organizations to manage their listings
3. **Favorites**: Allow users to save favorite adoption listings
4. **Notifications**: Notify users when new adoptions match their preferences
5. **Advanced Filtering**: Filter by species, breed, age, size, etc.
6. **Search History**: Track user search patterns for recommendations

## Testing

The implementation includes comprehensive test coverage for:

- Valid coordinate inputs with various radius values
- Invalid inputs (missing coordinates, invalid radius)
- Edge cases (extreme coordinates, boundary radius values)
- Error handling scenarios
- Database query optimization verification

See `test_nearby_adoptions_api.py` for detailed test cases and validation scenarios.

# Create Sighting API - Workflow Documentation

## Overview

The Create Sighting API implements a comprehensive workflow for animal sighting reporting with ML-powered species identification and profile matching. The system processes uploaded images, identifies species using external ML models, and matches sightings to existing animal profiles within a 10km radius.

## Workflow Steps

### 1. Initial Sighting Creation

**Endpoint:** `POST /api/animals/sightings/create/`

**Request:**

```json
{
  "image_url": "https://storage.bucket.com/animal-image.jpg",
  "longitude": -122.4194,
  "latitude": 37.7749
}
```

**What happens:**

1. Image URL and location are validated
2. Two ML APIs are called **concurrently**:
   - Species identification: `http://139.84.137.195:8001/identify-pet/`
   - Vector embedding generation: `http://139.84.137.195:8001/generate-embedding/`
3. AnimalMedia object is created with the embedding
4. AnimalSighting record is created (without animal profile link)
5. System searches for similar animal profiles within 10km using vector similarity
6. Matching profiles are returned to the user

**Response:**

```json
{
  "sighting": {
    "id": 123,
    "location": {
      "latitude": 37.7749,
      "longitude": -122.4194
    },
    "image": {
      "id": 456,
      "image_url": "https://storage.bucket.com/animal-image.jpg"
    },
    "reporter": {
      "id": 789,
      "username": "user123",
      "name": "John Doe"
    },
    "created_at": "2025-08-24T10:30:00Z",
    "status": "pending_profile_selection"
  },
  "ml_species_identification": {
    "species": "Dog",
    "breed": "Golden Retriever",
    "confidence": 0.89
  },
  "matching_profiles": [
    {
      "profile_id": 101,
      "animal_name": "Buddy",
      "species": "Dog",
      "breed": "Golden Retriever",
      "type": "stray",
      "similarity_score": 0.87,
      "distance_km": 2.3,
      "matching_image_url": "https://storage.bucket.com/buddy.jpg",
      "confidence": "high",
      "location": {
        "latitude": 37.785,
        "longitude": -122.41
      }
    }
  ],
  "profile_selection_required": true
}
```

### 2. Profile Selection/Creation

**Endpoint:** `POST /api/animals/sightings/select-profile/`

The user can either:

- **Select an existing matching profile**
- **Create a new stray animal profile**

#### Option A: Select Existing Profile

```json
{
  "sighting_id": 123,
  "action": "select_existing",
  "profile_id": 101
}
```

#### Option B: Create New Stray Profile

```json
{
  "sighting_id": 123,
  "action": "create_new",
  "new_profile_data": {
    "name": "Stray Golden",
    "species": "Dog",
    "breed": "Golden Retriever"
  }
}
```

**Response:**

```json
{
  "message": "Sighting linked to existing profile 'Buddy'",
  "sighting": {
    "id": 123,
    "animal": {
      "id": 101,
      "name": "Buddy",
      "species": "Dog",
      "breed": "Golden Retriever"
    },
    "location": {
      "latitude": 37.7749,
      "longitude": -122.4194
    },
    "created_at": "2025-08-24T10:30:00Z"
  },
  "animal_profile": {
    "id": 101,
    "name": "Buddy",
    "species": "Dog",
    "breed": "Golden Retriever",
    "type": "stray",
    "location": {
      "latitude": 37.785,
      "longitude": -122.41
    }
  }
}
```

## Technical Implementation

### ML API Integration

- **Concurrent Processing:** Both ML APIs are called simultaneously using ThreadPoolExecutor
- **Error Handling:** If either API fails, appropriate error messages are returned
- **Timeout:** 30-second timeout for ML API calls
- **Retry Logic:** Basic error handling with detailed logging

### Vector Similarity Matching

- **Database:** Uses pgvector extension for efficient vector similarity search
- **Algorithm:** Cosine similarity for comparing image embeddings
- **Filtering:**
  - Geographic: Within 10km radius using PostGIS
  - Similarity: Minimum threshold of 0.7 (configurable)
  - Limit: Maximum 10 results
- **Scoring:** Results include similarity scores and confidence levels

### Data Models

#### AnimalMedia

- Stores image URL and vector embedding (384 dimensions)
- Links to AnimalProfile (optional, for unlinked sightings)

#### AnimalSighting

- Links reporter, location, image, and animal profile
- Initially created without animal profile link
- Profile is linked after user selection

#### AnimalProfileModel

- Stores animal details (name, species, breed, type, location)
- Can be "pet" or "stray" type
- Links to owner (null for strays)

### Authentication

- Uses `UserTokenAuthentication`
- All endpoints require authenticated users
- Sightings are linked to the reporting user

### Input Validation

- **CreateSightingInputValidator:** Validates image URL and coordinates
- **SightingSelectProfileInputValidator:** Validates profile selection data
- Uses the existing GeneralValidator framework

### Error Handling

- ML API failures return appropriate error messages
- Invalid coordinates or image URLs are caught during validation
- Database errors are handled gracefully
- User permissions are checked (users can only modify their own sightings)

## Configuration

### ML API Settings

```python
ML_API_BASE_URL = "http://139.84.137.195:8001"
ML_API_TIMEOUT = 30
```

### Vector Search Settings

```python
DEFAULT_SEARCH_RADIUS_KM = 10
SIMILARITY_THRESHOLD = 0.7
MAX_MATCHING_PROFILES = 10
```

## Security Considerations

- Image URLs are validated but not sanitized (external storage assumed)
- User can only access their own sightings
- ML API calls are made server-side to protect API endpoints
- No sensitive data is stored in vector embeddings

## Performance Optimizations

- Concurrent ML API calls reduce response time by ~50%
- Vector similarity search uses HNSW index for efficiency
- Geographic filtering reduces vector search space
- Database queries are optimized with proper indexing

## Future Enhancements

1. **Caching:** Cache ML API results for identical images
2. **Batch Processing:** Process multiple sightings simultaneously
3. **Real-time Notifications:** Notify users of new sightings near their pets
4. **Advanced Matching:** Include temporal and behavioral patterns
5. **ML Model Updates:** Support for model versioning and A/B testing

## API Testing

Use the provided test script:

```bash
python3 test_sighting_api.py
```

This tests validation, serialization, and ML API connectivity without requiring a full Django server.

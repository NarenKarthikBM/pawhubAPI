# Lost Pets API Documentation

## Overview

The Lost Pets API allows pet owners to mark their pets as lost, which automatically creates both a lost pet report and an emergency post with the pet's last uploaded image. The system includes different emergency types for comprehensive animal care management.

## Emergency Types

The system supports the following emergency types:

1. **`injury`** - For animals that are injured and need medical attention
2. **`rescue_needed`** - For animals that need to be rescued from dangerous situations
3. **`aggressive_behavior`** - For animals displaying aggressive behavior that poses a risk
4. **`missing_lost_pet`** - For pets that are missing or lost (automatically set when marking pets as lost)

## Mark Pet as Lost Endpoint

### Endpoint

```
POST /api/animals/pets/mark-as-lost/
```

### Authentication

- Required: UserTokenAuthentication
- Include authentication token in the request headers
- Only pet owners can mark their own pets as lost

### Request Body

```json
{
  "pet_id": 123,
  "description": "My dog Buddy went missing during our evening walk in Central Park. He was wearing a red collar and is very friendly.",
  "last_seen_longitude": -73.9712,
  "last_seen_latitude": 40.7831,
  "last_seen_time": "2025-08-24T18:30:00Z"
}
```

### Required Fields

- `pet_id` (integer): ID of the pet to mark as lost
- `description` (string): Description of the circumstances (minimum 10 characters, maximum 1000 characters)

### Optional Fields

- `last_seen_longitude` (number): Longitude where pet was last seen
- `last_seen_latitude` (number): Latitude where pet was last seen
- `last_seen_time` (string): ISO datetime when pet was last seen (defaults to current time if not provided)

## Response

### Success Response (201 Created)

```json
{
  "lost_report": {
    "id": 45,
    "pet": {
      "id": 123,
      "name": "Buddy",
      "species": "Dog",
      "breed": "Golden Retriever",
      "type": "pet"
    },
    "description": "My dog Buddy went missing during our evening walk in Central Park. He was wearing a red collar and is very friendly.",
    "status": "active",
    "last_seen_location": {
      "latitude": 40.7831,
      "longitude": -73.9712
    },
    "last_seen_time": "2025-08-24T18:30:00Z",
    "created_at": "2025-08-24T19:00:00Z",
    "updated_at": "2025-08-24T19:00:00Z"
  },
  "emergency_post": {
    "id": 78,
    "emergency_type": "missing_lost_pet",
    "reporter": {
      "id": 1,
      "username": "petowner123",
      "name": "John Smith"
    },
    "location": {
      "latitude": 40.7831,
      "longitude": -73.9712
    },
    "image": {
      "id": 156,
      "image_url": "https://storage.vultr.com/pet-images/buddy-latest.jpg"
    },
    "animal": {
      "id": 123,
      "name": "Buddy",
      "species": "Dog",
      "breed": "Golden Retriever"
    },
    "description": "LOST PET: Buddy - My dog Buddy went missing during our evening walk in Central Park. He was wearing a red collar and is very friendly.",
    "status": "active",
    "created_at": "2025-08-24T19:00:00Z",
    "updated_at": "2025-08-24T19:00:00Z"
  },
  "message": "Buddy has been marked as lost and an emergency post has been created"
}
```

### Error Responses

#### 400 Bad Request - Validation Error

```json
{
  "error": "Description should have more than 10 and less than 1000 characters"
}
```

#### 400 Bad Request - Already Lost

```json
{
  "error": "Pet is already marked as lost"
}
```

#### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 404 Not Found - Pet Not Found

```json
{
  "error": "Pet not found or you don't have permission to mark it as lost"
}
```

## Emergency Creation Endpoint (Updated)

### Endpoint

```
POST /api/animals/emergencies/create/
```

### Request Body (Updated with Emergency Type)

```json
{
  "emergency_type": "injury",
  "longitude": 77.5946,
  "latitude": 12.9716,
  "description": "Injured dog found on the street, needs immediate medical attention",
  "image_url": "https://example.com/emergency-image.jpg"
}
```

### New Optional Field

- `emergency_type` (string): Type of emergency. Must be one of: `injury`, `rescue_needed`, `aggressive_behavior`, `missing_lost_pet`. Defaults to `injury` if not specified.

## Implementation Details

### Files Modified/Created

1. **animals/models.py** - Updated Emergency model with `emergency_type` field and `animal` relationship
2. **animals/validator.py** - Added `MarkPetAsLostInputValidator` and updated `CreateEmergencyInputValidator`
3. **animals/utils.py** - Added `mark_pet_as_lost()` utility function
4. **animals/views.py** - Added `MarkPetAsLostAPI` class
5. **animals/urls.py** - Added URL pattern for marking pets as lost
6. **animals/serializers.py** - Updated `EmergencySerializer` to include new fields

### Database Schema Updates

#### Emergency Model Updates

- Added `emergency_type` field with choices (default: "injury")
- Added `animal` field linking to AnimalProfileModel (for lost pet emergencies)

#### Lost Model

- `pet` (ForeignKey to AnimalProfileModel)
- `description` (TextField)
- `status` (CharField: 'active' or 'found')
- `last_seen_at` (PointField for GPS coordinates)
- `last_seen_time` (DateTimeField)
- `created_at` and `updated_at` (DateTimeFields)

### Validation Rules

#### Mark Pet as Lost

- Pet ID must be a valid integer
- User must own the pet
- Pet must be of type "pet" (not "stray")
- Pet cannot already be marked as lost
- Description must be 10-1000 characters
- Coordinates and time are optional but validated if provided

#### Emergency Creation (Updated)

- Emergency type must be one of the valid choices
- All existing validation rules apply

### Features

#### Automatic Emergency Post Creation

When a pet is marked as lost:

1. Creates a Lost report with pet details and circumstances
2. Automatically creates an Emergency post with type "missing_lost_pet"
3. Uses the pet's most recent uploaded image for the emergency post
4. Sets emergency location to last seen location (or pet's registered location as fallback)
5. Prefixes emergency description with "LOST PET: [Pet Name] - "

#### Enhanced Emergency System

- Emergency types provide better categorization for responders
- Lost pet emergencies are automatically linked to the pet profile
- Emergency posts include animal information when applicable

### Location Handling

- Uses WGS84 coordinate system (SRID 4326)
- Supports optional last seen location for lost pets
- Falls back to pet's registered location if last seen location not provided
- Comprehensive geographic indexing for location-based queries

### Security Features

- Only pet owners can mark their own pets as lost
- Authentication required for all operations
- Proper permission validation
- Prevention of duplicate lost reports for the same pet

## API Usage Examples

### Mark a Pet as Lost (Minimal)

```bash
curl -X POST "https://api.pawhub.com/api/animals/pets/mark-as-lost/" \
  -H "Authorization: Token your_auth_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "pet_id": 123,
    "description": "My cat Shadow escaped through the window and hasn't returned. She is very shy and may be hiding nearby."
  }'
```

### Mark a Pet as Lost (Complete)

```bash
curl -X POST "https://api.pawhub.com/api/animals/pets/mark-as-lost/" \
  -H "Authorization: Token your_auth_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "pet_id": 123,
    "description": "My dog Max ran off during a thunderstorm. He was last seen heading towards the forest trail.",
    "last_seen_longitude": -122.4194,
    "last_seen_latitude": 37.7749,
    "last_seen_time": "2025-08-24T20:15:00Z"
  }'
```

### Create Emergency with Type

```bash
curl -X POST "https://api.pawhub.com/api/animals/emergencies/create/" \
  -H "Authorization: Token your_auth_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "emergency_type": "rescue_needed",
    "longitude": 77.5946,
    "latitude": 12.9716,
    "description": "Cat stuck on tree branch about 15 feet high, appears distressed and unable to come down",
    "image_url": "https://example.com/cat-in-tree.jpg"
  }'
```

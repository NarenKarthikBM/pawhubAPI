# Pet Registration and Image Upload APIs

## Overview

This document describes the Pet Registration and Image Upload APIs for the PawHub platform. These APIs allow authenticated users to register their pets and upload images for their animals.

## Authentication

All endpoints require authentication using a Bearer token in the Authorization header:

```
Authorization: Token your_auth_token_here
```

## API Endpoints

### 1. Register Pet

**Endpoint:** `POST /api/animals/pets/register/`

**Description:** Register a new pet for the authenticated user.

**Request Body:**

```json
{
  "name": "Buddy",
  "species": "Dog",
  "breed": "Golden Retriever",
  "is_sterilized": true,
  "longitude": -122.4194,
  "latitude": 37.7749
}
```

**Required Fields:**

- `name` (string, max 255 chars): Pet name
- `species` (string, max 100 chars): Pet species

**Optional Fields:**

- `breed` (string, max 100 chars): Pet breed
- `is_sterilized` (boolean): Whether the pet is sterilized (default: false)
- `longitude` (number): Longitude coordinate
- `latitude` (number): Latitude coordinate

**Success Response (201):**

```json
{
  "success": true,
  "pet": {
    "id": 1,
    "name": "Buddy",
    "species": "Dog",
    "breed": "Golden Retriever",
    "type": "pet",
    "is_sterilized": true,
    "owner": {
      "id": 1,
      "username": "user123",
      "name": "John Doe"
    },
    "location": {
      "latitude": 37.7749,
      "longitude": -122.4194
    },
    "images": [],
    "breed_analysis": [],
    "created_at": "2023-01-01T12:00:00Z",
    "updated_at": "2023-01-01T12:00:00Z"
  }
}
```

**Error Response (400):**

```json
{
  "error": "Name is required"
}
```

### 2. Upload Image

**Endpoint:** `POST /api/animals/pets/upload/`

**Description:** Upload an image for a pet or as a standalone image.

**Content-Type:** `multipart/form-data`

**Form Fields:**

- `image_file` (file, required): Image file to upload (JPEG, PNG, WEBP, max 10MB)
- `animal_id` (integer, optional): Animal ID to link the image to

**Success Response (201):**

```json
{
  "success": true,
  "image": {
    "id": 1,
    "image_url": "https://storage.vultr.com/bucket/image123.jpg",
    "animal_id": 1,
    "uploaded_at": "2023-01-01T12:00:00Z"
  }
}
```

**Error Response (400):**

```json
{
  "error": "Image File is required"
}
```

## Usage Examples

### Example 1: Register a Pet with cURL

```bash
curl -X POST http://localhost:8000/api/animals/pets/register/ \
  -H "Authorization: Token your_auth_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Buddy",
    "species": "Dog",
    "breed": "Golden Retriever",
    "is_sterilized": true,
    "longitude": -122.4194,
    "latitude": 37.7749
  }'
```

### Example 2: Upload an Image with cURL

```bash
curl -X POST http://localhost:8000/api/animals/pets/upload/ \
  -H "Authorization: Token your_auth_token_here" \
  -F "image_file=@/path/to/your/image.jpg" \
  -F "animal_id=1"
```

### Example 3: Python Requests

```python
import requests

# Pet registration
pet_data = {
    "name": "Buddy",
    "species": "Dog",
    "breed": "Golden Retriever",
    "is_sterilized": True,
    "longitude": -122.4194,
    "latitude": 37.7749
}

headers = {
    "Authorization": "Token your_auth_token_here",
    "Content-Type": "application/json"
}

response = requests.post(
    "http://localhost:8000/api/animals/pets/register/",
    json=pet_data,
    headers=headers
)

print(response.json())

# Image upload
with open("pet_image.jpg", "rb") as image_file:
    files = {"image_file": image_file}
    data = {"animal_id": 1}

    headers = {"Authorization": "Token your_auth_token_here"}

    response = requests.post(
        "http://localhost:8000/api/animals/pets/upload/",
        files=files,
        data=data,
        headers=headers
    )

    print(response.json())
```

### Example 4: JavaScript/Fetch

```javascript
// Pet registration
const petData = {
  name: "Buddy",
  species: "Dog",
  breed: "Golden Retriever",
  is_sterilized: true,
  longitude: -122.4194,
  latitude: 37.7749,
};

fetch("/api/animals/pets/register/", {
  method: "POST",
  headers: {
    Authorization: "Token your_auth_token_here",
    "Content-Type": "application/json",
  },
  body: JSON.stringify(petData),
})
  .then((response) => response.json())
  .then((data) => console.log(data));

// Image upload
const formData = new FormData();
formData.append("image_file", fileInput.files[0]);
formData.append("animal_id", "1");

fetch("/api/animals/pets/upload/", {
  method: "POST",
  headers: {
    Authorization: "Token your_auth_token_here",
  },
  body: formData,
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

## Error Handling

### Common Error Responses

**401 Unauthorized:**

```json
{
  "error": "Authentication credentials were not provided"
}
```

**400 Bad Request - Validation Error:**

```json
{
  "error": "Name is required"
}
```

**400 Bad Request - File Upload Error:**

```json
{
  "error": "Image File size must be less than 10MB"
}
```

**400 Bad Request - Storage Error:**

```json
{
  "error": "Failed to upload image to storage"
}
```

## Validation Rules

### Pet Registration

- `name`: Required, string, 1-255 characters
- `species`: Required, string, 1-100 characters
- `breed`: Optional, string, max 100 characters
- `is_sterilized`: Optional, boolean
- `longitude`: Optional, number
- `latitude`: Optional, number

### Image Upload

- `image_file`: Required, valid image file (JPEG, PNG, WEBP), max 10MB
- `animal_id`: Optional, integer (must be owned by the authenticated user)

## Notes

1. **Geographic Data**: Location coordinates use WGS84 coordinate system (SRID 4326)
2. **Image Storage**: Images are stored in Vultr Object Storage and URLs are returned
3. **Pet Ownership**: Only the pet owner can upload images for their pets
4. **Image Linking**: If `animal_id` is not provided, the image is uploaded but not linked to any animal
5. **Vector Embeddings**: Images may be processed for similarity matching in the background

## Database Models

### AnimalProfileModel

- Stores pet profile information
- Links to CustomUser (owner)
- Supports geographic location data
- Can have multiple associated images

### AnimalMedia

- Stores image URLs and metadata
- Can be linked to AnimalProfileModel
- Supports vector embeddings for similarity matching
- Tracks upload timestamp

## Security Considerations

1. **Authentication**: All endpoints require valid user authentication
2. **File Validation**: Uploaded files are validated for type and size
3. **Ownership Verification**: Users can only link images to animals they own
4. **Input Sanitization**: All input data is validated and sanitized
5. **Storage Security**: Images are stored securely in Vultr Object Storage

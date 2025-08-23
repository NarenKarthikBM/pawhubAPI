# User Pets List API

## Overview

The User Pets List API endpoint allows authenticated users to retrieve a list of all pets they own.

## Endpoint

```
GET /api/animals/pets/my-pets/
```

## Authentication

- **Required**: Yes
- **Method**: Token-based authentication
- **Header**: `Authorization: Token your_token_here`

## Request

### Method: GET

No request parameters required. The API automatically filters pets based on the authenticated user.

### Headers

```
Authorization: Token your_auth_token_here
Content-Type: application/json
```

## Response

### Success Response (200 OK)

```json
{
  "success": true,
  "pets": [
    {
      "id": 1,
      "name": "Buddy",
      "species": "Dog",
      "breed": "Golden Retriever",
      "type": "pet",
      "is_sterilized": true,
      "images": [
        {
          "id": 1,
          "image_url": "https://storage.example.com/pets/buddy1.jpg"
        },
        {
          "id": 2,
          "image_url": "https://storage.example.com/pets/buddy2.jpg"
        }
      ],
      "location": {
        "latitude": 12.9716,
        "longitude": 77.5946
      },
      "created_at": "2023-08-24T10:30:00Z",
      "updated_at": "2023-08-24T10:30:00Z"
    },
    {
      "id": 2,
      "name": "Whiskers",
      "species": "Cat",
      "breed": "Persian",
      "type": "pet",
      "is_sterilized": false,
      "images": [],
      "location": null,
      "created_at": "2023-08-23T15:45:00Z",
      "updated_at": "2023-08-23T15:45:00Z"
    }
  ],
  "count": 2
}
```

### Error Responses

#### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 500 Internal Server Error

```json
{
  "error": "Failed to retrieve user pets: Database connection error"
}
```

## Response Fields

### Success Response Fields

- **success** (boolean): Indicates if the request was successful
- **pets** (array): Array of pet objects owned by the user
- **count** (integer): Total number of pets returned

### Pet Object Fields

- **id** (integer): Unique identifier for the pet
- **name** (string): Pet's name
- **species** (string): Pet's species (e.g., "Dog", "Cat")
- **breed** (string): Pet's breed
- **type** (string): Always "pet" for this endpoint
- **is_sterilized** (boolean): Whether the pet is sterilized
- **images** (array): Array of image objects associated with the pet
- **location** (object/null): Pet's location coordinates or null if not set
- **created_at** (string): ISO timestamp when the pet profile was created
- **updated_at** (string): ISO timestamp when the pet profile was last updated

### Image Object Fields

- **id** (integer): Unique identifier for the image
- **image_url** (string): URL to the image file

### Location Object Fields

- **latitude** (number): Latitude coordinate
- **longitude** (number): Longitude coordinate

## Usage Examples

### cURL Example

```bash
curl -X GET \
  http://localhost:8000/api/animals/pets/my-pets/ \
  -H 'Authorization: Token your_auth_token_here' \
  -H 'Content-Type: application/json'
```

### Python Example

```python
import requests

url = "http://localhost:8000/api/animals/pets/my-pets/"
headers = {
    "Authorization": "Token your_auth_token_here",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(f"Found {data['count']} pets:")
    for pet in data['pets']:
        print(f"- {pet['name']} ({pet['species']}, {pet['breed']})")
else:
    print(f"Error: {response.status_code}")
```

### JavaScript Example

```javascript
const fetchUserPets = async () => {
  try {
    const response = await fetch("/api/animals/pets/my-pets/", {
      method: "GET",
      headers: {
        Authorization: "Token your_auth_token_here",
        "Content-Type": "application/json",
      },
    });

    if (response.ok) {
      const data = await response.json();
      console.log(`Found ${data.count} pets:`, data.pets);
      return data.pets;
    } else {
      console.error("Failed to fetch pets:", response.statusText);
    }
  } catch (error) {
    console.error("Error fetching pets:", error);
  }
};
```

## Features

- **Authentication Required**: Only authenticated users can access their pets
- **User-specific**: Returns only pets owned by the authenticated user
- **Optimized Queries**: Uses `prefetch_related` for efficient database queries
- **Comprehensive Data**: Includes pet details, images, and location information
- **Ordered Results**: Pets are returned in reverse chronological order (newest first)
- **Error Handling**: Proper error responses for various failure scenarios

## Related Endpoints

- `POST /api/animals/pets/register/` - Register a new pet
- `POST /api/animals/pets/upload-images/` - Upload images for a pet
- `GET /api/animals/profiles/` - List all animal profiles (pets and strays)

## Notes

- The endpoint only returns animals with `type="pet"`
- Images are prefetched to avoid N+1 query problems
- Location data is optional and may be null
- The `breed_analysis` field from ML processing is not included in the user pets listing for brevity
- Empty arrays are returned for pets with no images

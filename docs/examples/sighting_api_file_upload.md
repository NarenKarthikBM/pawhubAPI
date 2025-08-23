# API Usage Example for Sighting Creation with File Upload

## Before Implementation (URL-based)

```python
# Previous approach with image URL
import requests

url = "http://localhost:8000/api/animals/sightings/"
headers = {
    "Authorization": "Token your_auth_token_here",
    "Content-Type": "application/json"
}
data = {
    "image_url": "https://example.com/path/to/animal/image.jpg",
    "longitude": -122.4194,
    "latitude": 37.7749
}

response = requests.post(url, json=data, headers=headers)
```

## After Implementation (File Upload)

```python
# New approach with direct file upload
import requests

url = "http://localhost:8000/api/animals/sightings/"
headers = {
    "Authorization": "Token your_auth_token_here"
    # Note: No Content-Type header needed for multipart/form-data
}

# Prepare form data
data = {
    "longitude": -122.4194,
    "latitude": 37.7749
}

# Open and upload the image file
with open('path/to/animal/image.jpg', 'rb') as image_file:
    files = {
        'image_file': image_file
    }
    response = requests.post(url, data=data, files=files, headers=headers)

print(response.json())
```

## JavaScript/Frontend Example

```javascript
// Frontend file upload example
const formData = new FormData();
formData.append("image_file", fileInput.files[0]);
formData.append("longitude", -122.4194);
formData.append("latitude", 37.7749);

fetch("/api/animals/sightings/", {
  method: "POST",
  headers: {
    Authorization: "Token your_auth_token_here",
  },
  body: formData,
})
  .then((response) => response.json())
  .then((data) => {
    console.log("Sighting created:", data);
  })
  .catch((error) => {
    console.error("Error:", error);
  });
```

## Response Format

The API response remains the same:

```json
{
    "sighting": {
        "id": 123,
        "reporter": {...},
        "location": {
            "type": "Point",
            "coordinates": [-122.4194, 37.7749]
        },
        "image": {
            "id": 456,
            "image_url": "https://ewr1.vultrobjects.com/your-bucket/sighting-images/abc123def456.jpg",
            "uploaded_at": "2025-01-24T10:30:00Z"
        },
        "created_at": "2025-01-24T10:30:00Z"
    },
    "ml_species_identification": {
        "species": "Dog",
        "breed": "Golden Retriever",
        "confidence": 0.95
    },
    "matching_profiles": [
        {
            "profile_id": 789,
            "name": "Buddy",
            "similarity_score": 0.87,
            "distance_km": 2.3
        }
    ],
    "profile_selection_required": true
}
```

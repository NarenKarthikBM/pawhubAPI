# API Usage Examples

## Authentication Examples

### User Registration and Login

```python
import requests

# Register new user
registration_data = {
    "email": "john.doe@example.com",
    "password": "securepassword123",
    "username": "johndoe",
    "name": "John Doe"
}

response = requests.post(
    "http://localhost:8000/api/users/register/",
    json=registration_data
)

if response.status_code == 201:
    user_data = response.json()
    auth_token = user_data['tokens']['auth_token']
    print(f"Registration successful! Token: {auth_token}")
else:
    print(f"Registration failed: {response.json()}")

# Login existing user
login_data = {
    "email": "john.doe@example.com",
    "password": "securepassword123"
}

response = requests.post(
    "http://localhost:8000/api/users/obtain-auth-token/",
    json=login_data
)

if response.status_code == 200:
    auth_data = response.json()
    auth_token = auth_data['tokens']['auth_token']
    print(f"Login successful! Token: {auth_token}")
```

## Emergency Reporting

### Create Emergency Report

```python
import requests

# Your authentication token
auth_token = "your_auth_token_here"

# Emergency data
emergency_data = {
    "longitude": 77.5946,  # Bangalore coordinates
    "latitude": 12.9716,
    "description": "Injured stray dog found near MG Road metro station. Animal appears to have a broken leg and needs immediate veterinary attention.",
    "image_url": "https://example.com/emergency-photos/injured-dog-001.jpg"
}

headers = {
    "Authorization": f"Token {auth_token}",
    "Content-Type": "application/json"
}

response = requests.post(
    "http://localhost:8000/api/animals/emergencies/",
    json=emergency_data,
    headers=headers
)

if response.status_code == 201:
    emergency = response.json()
    print(f"Emergency created successfully!")
    print(f"Emergency ID: {emergency['emergency']['id']}")
    print(f"Status: {emergency['emergency']['status']}")
else:
    print(f"Failed to create emergency: {response.json()}")
```

### Find Nearby Emergencies

```python
import requests

# Your location coordinates
latitude = 12.9716
longitude = 77.5946

headers = {
    "Authorization": f"Token {auth_token}"
}

params = {
    "latitude": latitude,
    "longitude": longitude
}

response = requests.get(
    "http://localhost:8000/api/animals/emergencies/nearby/",
    params=params,
    headers=headers
)

if response.status_code == 200:
    emergencies = response.json()
    print(f"Found {len(emergencies)} nearby emergencies:")

    for emergency in emergencies:
        print(f"- Emergency #{emergency['id']}")
        print(f"  Description: {emergency['description'][:50]}...")
        print(f"  Status: {emergency['status']}")
        print(f"  Reporter: {emergency['reporter']['name']}")
        print(f"  Created: {emergency['created_at']}")
        print()
else:
    print(f"Failed to fetch emergencies: {response.json()}")
```

## Animal Profile Management

### List Animal Profiles

```python
import requests

headers = {
    "Authorization": f"Token {auth_token}"
}

# Optional filters
params = {
    "type": "stray",  # Filter by animal type
    "species": "dog"  # Filter by species
}

response = requests.get(
    "http://localhost:8000/api/animals/profiles/",
    params=params,
    headers=headers
)

if response.status_code == 200:
    profiles = response.json()
    print(f"Found {len(profiles)} animal profiles:")

    for profile in profiles:
        print(f"- {profile['name']} ({profile['species']})")
        print(f"  Type: {profile['type']}")
        print(f"  Breed: {profile['breed']}")
        if profile['location']:
            print(f"  Location: {profile['location']['latitude']}, {profile['location']['longitude']}")
        print()
```

## Organization Management

### Organization Registration

```python
import requests

org_data = {
    "name": "Mumbai Animal Welfare Society",
    "email": "contact@maws.org",
    "password": "secureorgpassword123",
    "phone": "+91-9876543210",
    "address": "123 Animal Street, Mumbai, Maharashtra",
    "latitude": 19.0760,
    "longitude": 72.8777,
    "website": "https://maws.org",
    "registration_number": "ORG/2023/001"
}

response = requests.post(
    "http://localhost:8000/api/organisations/register/",
    json=org_data
)

if response.status_code == 201:
    org_result = response.json()
    print("Organization registered successfully!")
    print(f"Organization ID: {org_result['organisation']['id']}")
    print(f"Verification Status: {org_result['organisation']['is_verified']}")
else:
    print(f"Registration failed: {response.json()}")
```

## Veterinarian Management

### Veterinarian Registration

```python
import requests

vet_data = {
    "email": "dr.smith@vetclinic.com",
    "password": "securevetpassword123",
    "name": "Dr. John Smith",
    "phone": "+91-9876543210",
    "license_number": "VET/KA/2023/001",
    "specialization": "Small Animal Medicine",
    "experience_years": 8,
    "clinic_name": "City Veterinary Clinic",
    "clinic_address": "456 Health Street, Bangalore, Karnataka",
    "latitude": 12.9716,
    "longitude": 77.5946
}

response = requests.post(
    "http://localhost:8000/api/vets/register/",
    json=vet_data
)

if response.status_code == 201:
    vet_result = response.json()
    print("Veterinarian registered successfully!")
    print(f"Vet ID: {vet_result['vet']['id']}")
    print(f"License: {vet_result['vet']['license_number']}")
else:
    print(f"Registration failed: {response.json()}")
```

## Error Handling

### Comprehensive Error Handling

```python
import requests
from requests.exceptions import RequestException

def make_api_request(url, method='GET', data=None, auth_token=None):
    """
    Generic function to make API requests with proper error handling
    """
    headers = {"Content-Type": "application/json"}

    if auth_token:
        headers["Authorization"] = f"Token {auth_token}"

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)

        # Check for HTTP errors
        if response.status_code >= 400:
            error_data = response.json() if response.content else {}
            print(f"API Error ({response.status_code}): {error_data}")
            return None

        return response.json()

    except RequestException as e:
        print(f"Network error: {e}")
        return None
    except ValueError as e:
        print(f"JSON decode error: {e}")
        return None

# Example usage
result = make_api_request(
    "http://localhost:8000/api/animals/emergencies/",
    method='POST',
    data=emergency_data,
    auth_token=auth_token
)

if result:
    print("Request successful:", result)
else:
    print("Request failed")
```

## JavaScript/Frontend Examples

### Using Fetch API

```javascript
class PawHubAPI {
  constructor(baseURL = "http://localhost:8000/api/", authToken = null) {
    this.baseURL = baseURL;
    this.authToken = authToken;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    if (this.authToken) {
      config.headers["Authorization"] = `Token ${this.authToken}`;
    }

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "API request failed");
      }

      return await response.json();
    } catch (error) {
      console.error("API Error:", error);
      throw error;
    }
  }

  async register(userData) {
    return await this.request("users/register/", {
      method: "POST",
      body: JSON.stringify(userData),
    });
  }

  async createEmergency(emergencyData) {
    return await this.request("animals/emergencies/", {
      method: "POST",
      body: JSON.stringify(emergencyData),
    });
  }

  async getNearbyEmergencies(latitude, longitude) {
    const params = new URLSearchParams({
      latitude: latitude.toString(),
      longitude: longitude.toString(),
    });

    return await this.request(`animals/emergencies/nearby/?${params}`);
  }
}

// Usage example
const api = new PawHubAPI();

// Register user
try {
  const registrationResult = await api.register({
    email: "user@example.com",
    password: "password123",
    username: "username",
    name: "User Name",
  });

  // Set auth token for subsequent requests
  api.authToken = registrationResult.tokens.auth_token;

  // Create emergency
  const emergency = await api.createEmergency({
    longitude: 77.5946,
    latitude: 12.9716,
    description: "Emergency description",
  });

  console.log("Emergency created:", emergency);
} catch (error) {
  console.error("Operation failed:", error.message);
}
```

## Testing Examples

### Unit Test Examples

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class EmergencyAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            name='Test User',
            password='testpass123'
        )

    def test_create_emergency_success(self):
        """Test successful emergency creation"""
        self.client.force_authenticate(user=self.user)

        data = {
            'longitude': 77.5946,
            'latitude': 12.9716,
            'description': 'Test emergency description that is long enough'
        }

        response = self.client.post('/api/animals/emergencies/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('emergency', response.data)
        self.assertEqual(response.data['emergency']['description'], data['description'])

    def test_create_emergency_unauthenticated(self):
        """Test emergency creation without authentication"""
        data = {
            'longitude': 77.5946,
            'latitude': 12.9716,
            'description': 'Test emergency description'
        }

        response = self.client.post('/api/animals/emergencies/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_emergency_invalid_data(self):
        """Test emergency creation with invalid data"""
        self.client.force_authenticate(user=self.user)

        data = {
            'longitude': 'invalid',
            'latitude': 12.9716,
            'description': 'short'  # Too short
        }

        response = self.client.post('/api/animals/emergencies/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
```

This comprehensive examples file demonstrates:

1. **Authentication workflows** - Registration and login
2. **Emergency management** - Creating and finding emergencies
3. **Animal profile management** - Listing and filtering
4. **Organization and vet registration**
5. **Proper error handling** - Network errors, API errors, validation errors
6. **Frontend integration** - JavaScript/Fetch API examples
7. **Testing patterns** - Unit test examples

Each example includes proper error handling and follows the API patterns established in the codebase.

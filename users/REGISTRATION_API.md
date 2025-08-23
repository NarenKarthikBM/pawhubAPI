# User Registration API Documentation

## Overview

The User Registration API allows new users to create accounts on the PawHub platform without requiring OTP verification. Upon successful registration, users receive authentication tokens that can be used for subsequent API calls.

## Endpoint

```
POST /api/users/register/
```

## Request Format

### Headers

```
Content-Type: application/json
```

### Request Body

```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "username": "unique_username",
  "name": "User Full Name"
}
```

### Field Validation Rules

| Field      | Type   | Required | Validation Rules                                |
| ---------- | ------ | -------- | ----------------------------------------------- |
| `email`    | string | Yes      | Must be valid email format with @ symbol        |
| `password` | string | Yes      | Minimum 8 characters, maximum 100 characters    |
| `username` | string | Yes      | 3-20 characters, must be unique across platform |
| `name`     | string | Yes      | 1-50 characters, user's full name               |

## Response Format

### Success Response (201 Created)

```json
{
  "tokens": {
    "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "device_token": "device_abc123"
  },
  "user_details": {
    "id": 1,
    "name": "User Full Name",
    "email": "user@example.com",
    "username": "unique_username",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false,
    "date_joined": "2025-08-23T10:30:00Z"
  }
}
```

### Error Response (400 Bad Request)

#### Email Already Exists

```json
{
  "error": "User with this email already exists",
  "field": "email"
}
```

#### Username Already Exists

```json
{
  "error": "User with this username already exists",
  "field": "username"
}
```

#### Validation Error

```json
{
  "error": "Password must be at least 8 characters long",
  "field": "password"
}
```

## Usage Examples

### cURL Example

```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "securepassword123",
    "username": "newuser",
    "name": "New User"
  }'
```

### Python requests Example

```python
import requests

data = {
    "email": "newuser@example.com",
    "password": "securepassword123",
    "username": "newuser",
    "name": "New User"
}

response = requests.post(
    "http://localhost:8000/api/users/register/",
    json=data
)

if response.status_code == 201:
    result = response.json()
    auth_token = result['tokens']['auth_token']
    print(f"Registration successful! Auth token: {auth_token}")
else:
    error = response.json()
    print(f"Registration failed: {error['error']}")
```

### JavaScript/Fetch Example

```javascript
const registrationData = {
  email: "newuser@example.com",
  password: "securepassword123",
  username: "newuser",
  name: "New User",
};

fetch("/api/users/register/", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(registrationData),
})
  .then((response) => response.json())
  .then((data) => {
    if (data.tokens) {
      console.log("Registration successful!", data);
      // Store tokens for future API calls
      localStorage.setItem("authToken", data.tokens.auth_token);
    } else {
      console.error("Registration failed:", data.error);
    }
  });
```

## Authentication

After successful registration, the response includes authentication tokens:

- **auth_token**: Used for authenticating API requests
- **device_token**: Used for device-specific operations

To authenticate subsequent API calls, include the auth_token in the Authorization header:

```
Authorization: Token your_auth_token_here
```

## Implementation Details

### Database Schema

The registration process creates a new `CustomUser` record with:

- Email-based authentication (unique)
- Username (unique, 3-20 characters)
- Encrypted password using Django's built-in password hashing
- User profile information (name)
- Timestamp fields (date_joined, etc.)

### Token Management

- Tokens are generated using secure random generation
- `UserAuthTokens` record created linking user to tokens
- Token type set to "web" by default
- Tokens are unique across the platform

### Security Features

- Password validation (minimum length enforcement)
- Email format validation
- Username uniqueness validation
- Secure password hashing
- Token-based authentication

## Related Endpoints

- **Login**: `POST /api/users/obtain-auth-token/` - Authenticate existing users
- **User Profile**: `GET /api/users/profile/` - Retrieve user profile (requires auth)

## Error Handling

The API follows RESTful error handling conventions:

- 201: Successful registration
- 400: Validation errors or duplicate data
- 500: Internal server error

All error responses include:

- `error`: Human-readable error message
- `field`: Field that caused the validation error (when applicable)

## Testing

Run the registration API tests:

```bash
python manage.py test users.test_registration
```

## Swagger Documentation

The registration API is fully documented in the Swagger/OpenAPI specification available at:

```
http://localhost:8000/swagger/
```

The Swagger documentation includes:

- Interactive API testing interface
- Request/response examples
- Field validation rules
- Error response examples

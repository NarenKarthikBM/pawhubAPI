# API Documentation Index

## Available API Endpoints

### 🐾 Animals Module (`/api/animals/`)

#### Emergency Management

- **[POST /animals/emergencies/](emergency.md)** - Create Emergency Report
  - Create new emergency reports with location and description
  - Requires authentication
  - Supports optional image attachment

#### Animal Profiles

- **GET /animals/profiles/** - List Animal Profiles
  - Filter by type (pet/stray) and species
  - Paginated results with search capability

#### Pet Management

- **[GET /animals/pets/my-pets/](user-pets-list.md)** - List User's Pets
  - Get all pets owned by authenticated user
  - Includes pet details, images, and location
  - Requires authentication

- **POST /animals/pets/register/** - Register New Pet
  - Add new pet to user's profile
  - Supports breed analysis and location data

- **POST /animals/pets/upload-images/** - Upload Pet Images
  - Add images to existing pet profiles
  - Supports multiple image uploads

#### Location-Based Services

- **GET /animals/emergencies/nearby/** - Get Nearby Emergencies

  - Find active emergencies within 20km radius
  - Requires latitude/longitude coordinates

- **GET /animals/sightings/nearby/** - Get Nearby Sightings
  - Find animal sightings in specified area
  - Geographic search with distance filtering

### 👥 Users Module (`/api/users/`)

#### Authentication

- **[POST /users/register/](user-registration.md)** - User Registration

  - Create new user accounts
  - Returns authentication tokens
  - Email-based authentication

- **POST /users/obtain-auth-token/** - User Login
  - Authenticate existing users
  - Returns auth and device tokens

#### Profile Management

- **GET /users/profile/** - Get User Profile
  - Retrieve current user information
  - Requires authentication

### 🏢 Organizations Module (`/api/organisations/`)

#### Organization Management

- **POST /organisations/register/** - Organization Registration

  - Register animal welfare organizations
  - Includes verification workflow
  - Location-based services

- **POST /organisations/obtain-auth-token/** - Organization Login
  - Organization authentication
  - Separate token system

### 🩺 Veterinarians Module (`/api/vets/`)

#### Veterinarian Management

- **POST /vets/register/** - Veterinarian Registration

  - Professional vet account creation
  - License number validation
  - Clinic information management

- **POST /vets/obtain-auth-token/** - Veterinarian Login
  - Vet authentication system
  - Professional account access

## Authentication

### Token-Based Authentication

All protected endpoints require an authentication token in the header:

```
Authorization: Token your_auth_token_here
```

### Authentication Flow

1. **Register** - Create account using registration endpoints
2. **Login** - Obtain authentication tokens
3. **API Access** - Include token in subsequent requests

## Common Patterns

### Request Format

```json
{
  "field1": "value1",
  "field2": "value2"
}
```

### Success Response Format

```json
{
  "data": {...},
  "message": "Operation successful"
}
```

### Error Response Format

```json
{
  "error": "Human-readable error message",
  "field": "field_name_if_applicable"
}
```

### Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `404` - Not Found
- `500` - Internal Server Error

## Geographic Features

### Location Data Format

```json
{
  "latitude": 12.9716,
  "longitude": 77.5946
}
```

### Distance-Based Queries

- Emergency search: 20km radius
- Sighting search: Configurable radius
- Organization discovery: Location-based

## Field Validation

### Common Validation Rules

- **Email**: Must contain @ symbol and valid format
- **Password**: Minimum 8 characters, maximum 100
- **Coordinates**: Valid latitude (-90 to 90) and longitude (-180 to 180)
- **Descriptions**: Minimum 10 characters for emergency reports

### Required vs Optional Fields

Each endpoint documentation specifies:

- Required fields (must be provided)
- Optional fields (can be omitted)
- Default values where applicable

## Interactive Documentation

### Swagger/OpenAPI

Access the interactive API documentation at:

```
http://localhost:8000/swagger/
```

Features:

- Live API testing
- Request/response examples
- Authentication testing
- Complete schema documentation

## Examples and Tutorials

See [API Usage Examples](../examples/api-usage.md) for:

- Code examples in Python and JavaScript
- Authentication workflows
- Error handling patterns
- Frontend integration examples
- Testing patterns

## Support

### Testing

```bash
# Run API tests
python manage.py test

# Test specific modules
python manage.py test animals
python manage.py test users
```

### Development

See [Development Setup](../development/setup.md) for local development configuration.

### Deployment

See [Deployment Guide](../deployment/production.md) for production deployment instructions.

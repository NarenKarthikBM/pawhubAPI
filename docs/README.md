# PawHub API Documentation

## Overview

PawHub API is a comprehensive Django REST Framework-based platform for animal care and management. The API enables users to manage animal profiles, track lost pets, coordinate adoptions, connect with veterinarians, and work with animal welfare organizations.

## Quick Start

### Base URL

```
http://localhost:8000/api/
```

### Authentication

Most endpoints require authentication using Token-based authentication:

```
Authorization: Token your_auth_token_here
```

## API Modules

### 🐾 Animals (`/api/animals/`)

Manage animal profiles, sightings, emergencies, lost pets, and adoptions.

### 👥 Users (`/api/users/`)

User registration, authentication, and profile management.

### 🏢 Organizations (`/api/organisations/`)

Animal welfare organization management and verification.

### 🩺 Veterinarians (`/api/vets/`)

Veterinary professional profiles and services.

## Documentation Structure

```
docs/
├── README.md                 # This file
├── api/                      # API endpoint documentation
│   ├── emergency.md         # Emergency reporting API
│   ├── user-registration.md # User registration API
│   └── ...                  # Additional API docs
├── deployment/              # Deployment guides
├── development/             # Development setup
└── examples/               # Code examples and tutorials
```

## API Documentation

### Available Endpoints

#### Animals Module

- **POST** `/animals/emergencies/` - [Create Emergency Report](api/emergency.md)
- **GET** `/animals/emergencies/nearby/` - Get Nearby Emergencies
- **GET** `/animals/profiles/` - List Animal Profiles
- **GET** `/animals/sightings/nearby/` - Get Nearby Sightings

#### Users Module

- **POST** `/users/register/` - [User Registration](api/user-registration.md)
- **POST** `/users/obtain-auth-token/` - User Login
- **GET** `/users/profile/` - Get User Profile

#### Organizations Module

- **POST** `/organisations/register/` - Organization Registration
- **POST** `/organisations/obtain-auth-token/` - Organization Login

#### Veterinarians Module

- **POST** `/vets/register/` - Veterinarian Registration
- **POST** `/vets/obtain-auth-token/` - Veterinarian Login

## Features

### 🌍 Geographic Services

- Location-based queries using PostGIS
- Nearby emergency and sighting discovery
- Coordinate-based animal tracking

### 🔍 Search & Discovery

- Full-text search with PostgreSQL
- Vector embeddings for media similarity
- Advanced filtering and pagination

### 🔐 Multi-Entity Authentication

- User authentication system
- Organization verification workflow
- Veterinarian license validation

### 📊 Rich Media Support

- Image and video upload handling
- Vector embeddings for similarity matching
- URL-based media storage

## Getting Started

### 1. Authentication

First, register a new user account:

```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "username": "myusername",
    "name": "My Name"
  }'
```

### 2. Use Authentication Token

Include the returned token in subsequent requests:

```bash
curl -X GET http://localhost:8000/api/animals/profiles/ \
  -H "Authorization: Token your_auth_token_here"
```

### 3. Report an Emergency

Create an emergency report with location:

```bash
curl -X POST http://localhost:8000/api/animals/emergencies/ \
  -H "Authorization: Token your_auth_token_here" \
  -H "Content-Type: application/json" \
  -d '{
    "longitude": 77.5946,
    "latitude": 12.9716,
    "description": "Injured animal needs help"
  }'
```

## Interactive Documentation

### Swagger/OpenAPI

Access the interactive API documentation at:

```
http://localhost:8000/swagger/
```

The Swagger interface provides:

- Interactive API testing
- Complete endpoint documentation
- Request/response examples
- Authentication testing

## Development

### Tech Stack

- **Framework**: Django 4.x + Django REST Framework
- **Database**: PostgreSQL with PostGIS
- **Authentication**: Token-based
- **Documentation**: drf-yasg (Swagger/OpenAPI)
- **Geographic**: GeoDjango for location services
- **Search**: PostgreSQL full-text search + vector embeddings

### Local Setup

```bash
# Clone repository
git clone <repository-url>
cd pawhubAPI

# Install dependencies
pipenv install

# Activate virtual environment
pipenv shell

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## Support

### Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test animals
python manage.py test users
```

### Error Handling

All APIs follow consistent error response format:

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

## Contributing

1. Follow the existing code patterns and conventions
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Use custom APIViews and serializers (not ModelViewSets)
5. Include Swagger documentation for all endpoints

## License

[Add license information here]

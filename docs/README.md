# PawHub API Documentation

## Overview

PawHub API is a comprehensive Django REST Framework-based platform for animal care and management. The API enables users to manage animal profiles, track lost pets, coordinate adoptions, connect with veterinarians, and work with animal welfare organizations.

## Quick Start

### Base URL

```
https://pawhub.ddns.net
```

### Swagger Docs
```
https://pawhub.ddns.net/swagger
```

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
- Organization authentication workflow
- Veterinarian authentication workflow

### 📊 Rich Media Support

- Image upload handling
- Vector embeddings for similarity matching
- URL-based media storage

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

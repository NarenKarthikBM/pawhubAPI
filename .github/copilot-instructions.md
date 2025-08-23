# GitHub Copilot Instructions for PawHub API

## Project Overview

PawHub API is a Django REST Framework-based animal care and management platform API that enables users to manage animal profiles, track lost pets, coordinate adoptions, connect with veterinarians, and work with animal welfare organizations. The API follows REST principles and includes comprehensive OpenAPI/Swagger documentation.

## Architecture & Tech Stack

- **Framework**: Django 4.x + Django REST Framework
- **Database**: PostgreSQL with GeoDjango (PostGIS) for geographic data
- **Authentication**: Token-based authentication
- **Documentation**: drf-yasg (Swagger/OpenAPI)
- **Geographic Features**: Django GIS for location-based services
- **Deployment**: Docker containerization
- **Environment Management**: Pipenv

## API Endpoints

### Core Modules

#### 1. Users (`/api/users/`)

- **Authentication**: Registration, login, logout, token management
- **Profile Management**: User profile CRUD operations with custom user model
- **Custom User Model**: Email-based authentication with username and name fields
- **Token Management**: Custom token generation and management

#### 2. Animals (`/api/animals/`)

- **Animal Profiles**: CRUD operations for pet and stray animal profiles
- **Media Management**: Image/video upload with URL storage and vector embeddings
- **Lost Animals**: Track and manage lost pet reports
- **Adoptions**: Coordinate animal adoption processes
- **Sightings**: Record animal sightings with location data
- **Emergencies**: Handle animal emergency situations
- **Geographic Features**: Location-based services using PostGIS

#### 3. Organizations (`/api/organisations/`)

- **Organization Management**: CRUD operations for animal welfare organizations
- **Verification System**: Organization verification workflow
- **Location Services**: Geographic location support with coordinates
- **Token Management**: Organization-specific authentication tokens

#### 4. Veterinarians (`/api/vets/`)

- **Vet Profiles**: Professional veterinarian profile management
- **License Verification**: Veterinary license number tracking
- **Specializations**: Track veterinary specializations and experience
- **Clinic Information**: Manage clinic details and locations
- **Geographic Services**: Location-based vet discovery
- **Appointments**: Veterinary appointment scheduling system
- **Reviews**: Vet review and rating system

## Authentication

All authenticated endpoints require a Token in the Authorization header:

```
Authorization: Token your_token_here
```

The platform supports multiple authentication entities:

- **Users**: Custom user model with email-based authentication
- **Organizations**: Separate token system for organization accounts
- **Veterinarians**: Professional vet account authentication

## Code Standards

### API Design

1. **Use custom APIViews** to implement CRUD operations
2. **Implement proper custom serializers**
3. **Focus on creating performance optimized views** using custom serializers
4. **Add Swagger documentation** to all endpoints using `@swagger_auto_schema`
5. **Use appropriate HTTP status codes**
6. **Implement proper error handling**

### Model Design

1. **Use PostgreSQL features**: Full-text search, arrays, JSON fields, PostGIS for geographic data
2. **Add proper indexing** for search fields and geographic queries
3. **Include audit fields**: created_at, updated_at, date_joined
4. **Use proper relationships** with related_name and related_query_name
5. **Implement GeoDjango**: Use PointField for location-based services
6. **Vector Embeddings**: Support for similarity matching in media files

## Development Workflow

### Branch Strategy

- **main**: Production-ready code
- **staging**: Testing and staging environment
- **feature/**: Feature development branches
- **hotfix/**: Critical bug fixes

### Local Development

```bash
# Install dependencies
pipenv install

# Activate virtual environment
pipenv shell

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Testing

```bash
# Run tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test animals
python manage.py test organisations
python manage.py test vets
```

### Deployment

```bash
# Build Docker container
docker build -t pawhub-api .

# Run with Docker Compose
docker-compose up
```

## Database

### Search Implementation

- Use PostgreSQL full-text search with `SearchVectorField`
- Index search vectors with GIN indexes
- Implement search ranking with weights
- Use GeoDjango for location-based queries

### Geographic Features

```python
# Location field setup
location = models.PointField(
    srid=4326,  # WGS84 coordinate system
    null=True,
    blank=True,
)

# Geographic queries
nearby_vets = Vet.objects.filter(
    location__distance_lte=(user_location, D(km=10))
)
```

### Vector Embeddings

```python
# Vector field for similarity matching
embedding = VectorField(
    dimensions=384,  # Standard for sentence-transformers
    null=True,
    blank=True,
)
```

### Common Patterns

```python
# Full-text search setup
search_vector = SearchVectorField(null=True)

class Meta:
    indexes = [
        GinIndex(fields=["search_vector"]),
    ]
```

## API Documentation Best Practices

### Swagger Documentation

1. **Add operation descriptions** that explain what the endpoint does
2. **Document all parameters** with types and descriptions
3. **Include example responses** for different status codes
4. **Use proper tags** to group related endpoints
5. **Document authentication requirements**

### Response Formats

```python
# Standard success response
{
    "id": 1,
    "field": "value",
    "created_at": "2023-01-01T00:00:00Z"
}

# Standard error response
{
    "error": "Error message",
    "detail": "Detailed error description"
}

# Paginated list response
{
    "count": 100,
    "next": "http://api.example.com/page=2",
    "previous": null,
    "results": [...]
}
```

## Security Considerations

1. **Always validate input** in serializers
2. **Use proper permissions** on all endpoints
3. **Implement rate limiting** for public endpoints
4. **Sanitize file uploads** in media handling
5. **Use HTTPS** in production
6. **Rotate secrets regularly**

## Performance Optimization

1. **Use select_related/prefetch_related** for database queries
2. **Implement pagination** for list endpoints
3. **Add database indexes** for frequently queried fields
4. **Use caching** for static or slow data
5. **Optimize image uploads** with compression

## Monitoring & Logging

1. **Log all API errors** with context
2. **Monitor response times** and error rates
3. **Track user actions** for analytics
4. **Set up alerts** for critical failures

## Common Patterns to Follow

### Error Handling

```python
try:
    # Operation
    pass
except SpecificException as e:
    return Response(
        {'error': 'User-friendly message'},
        status=status.HTTP_400_BAD_REQUEST
    )
```

### Filtering and Search

```python
class ModelViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['field1', 'field2']
    search_fields = ['title', 'description']
```

### Custom Actions

```python
@action(detail=True, methods=['post'])
def custom_action(self, request, pk=None):
    obj = self.get_object()
    # Custom logic
    return Response(data)
```

## **CRITICAL PERFORMANCE GUIDELINES**

### **Custom Implementation Requirements**

**ALWAYS use these patterns - DO NOT use standard DRF ModelSerializers/ViewSets:**

1. **Custom APIView Classes**: Create custom APIView classes instead of using ViewSets or generic views
2. **Custom Serializer Classes**: Write custom serializer classes, NOT ModelSerializers
3. **Custom Validation Classes**: Create separate validation classes for input validation
4. **Performance Optimization**: Focus on performance-optimized code with minimal database queries

### **File Structure Requirements**

- **ONLY use**: `urls.py`, `views.py`, `serializers.py`, `validator.py`, `utils.py`
- **DO NOT create**: `api_urls.py`, `api_views.py`, or other separate API files
- **Consolidate**: All API views must go in `views.py`
- **Consolidate**: All URL patterns must go in `urls.py`

### **Code Pattern Examples**

#### Custom APIView Pattern:

```python
class UserObtainAuthTokenAPI(APIView):
    """API view to obtain auth tokens

    Methods:
        POST
    """

    permission_classes = []
    authentication_classes = []

    def post(self, request):
        validated_data = UserObtainAuthTokenInputValidator(
            request.data
        ).serialized_data()

        user_authorization = authorize_user(validated_data)
        return Response(user_authorization, status=status.HTTP_200_OK)
```

#### Custom Serializer Pattern:

```python
class UserSerializer:
    """This serializer class contains serialization methods for User Model"""

    def __init__(self, obj: models.CustomUser):
        self.obj = obj

    def details_serializer(self):
        return {
            "id": self.obj.id,
            "name": self.obj.name,
            "email": self.obj.email,
            # ... other fields
        }
```

#### Custom Validator Pattern:

```python
class UserObtainAuthTokenInputValidator(GeneralValidator):
    def __init__(self, data) -> None:
        self.data = data

    def serialized_data(self):
        email, password = self.data.get("email"), self.data.get("password")
        return {
            "email": self.validate_data(
                email,
                self.validate_type("Email", email, str)
                or self.validate_contains("Email", email, ["@"]),
                "email",
            ),
            "password": self.validate_data(
                password,
                self.validate_type("Password", password, str),
                "password"
            ),
        }
```

#### Utility Function Pattern:

```python
def authorize_user(data):
    user = CustomUser.objects.filter(email=data["email"]).first()

    if not user:
        return None

    if not user.check_password(data["password"]):
        return {"error": "Invalid Password"}

    tokens = generate_tokens()
    # ... rest of logic

    return {
        "tokens": tokens,
        "user_details": UserSerializer(user).details_serializer(),
    }
```

### **API Endpoint Naming**

Use descriptive, action-based endpoint names consistent with current patterns:

**Authentication endpoints:**

- `obtain-auth-token/` for login (users, organisations, vets)
- `register/` for registration (organisations, vets)
- `verification/` for verification processes

**Animal endpoints:**

- `profiles/` for animal profile management
- `sightings/` for animal sighting reports
- `emergencies/` for emergency situations
- `lost/` for lost pet management
- `adoptions/` for adoption coordination

### **Performance Guidelines**

1. **Database Queries**: Use `select_related()` and `prefetch_related()` appropriately
2. **Custom Serializers**: Write specific serialization methods instead of using ModelSerializer
3. **Validation**: Create dedicated validator classes for input validation
4. **Utils**: Extract business logic into utility functions
5. **Error Handling**: Use custom error responses with appropriate HTTP status codes
6. **Geographic Queries**: Optimize location-based queries with proper indexing
7. **Vector Operations**: Use efficient vector similarity searches for media matching

### **NEVER DO:**

- ❌ Use ModelSerializer or ModelViewSet
- ❌ Create separate api_views.py or api_urls.py files
- ❌ Use generic DRF views when custom performance is needed
- ❌ Skip custom validation classes
- ❌ Put business logic directly in view methods
- ❌ Ignore geographic indexing for location-based queries
- ❌ Store sensitive veterinary or organization data without proper validation

### **ALWAYS DO:**

- ✅ Use custom APIView classes
- ✅ Create custom serializer classes with specific methods (details_serializer, condensed_details_serializer)
- ✅ Write dedicated validator classes extending GeneralValidator
- ✅ Extract business logic to utility functions
- ✅ Follow the established code patterns
- ✅ Optimize for performance over convenience
- ✅ Use GeoDjango for all location-based features
- ✅ Implement proper vector embeddings for media similarity matching
- ✅ Include comprehensive Swagger documentation for all endpoints

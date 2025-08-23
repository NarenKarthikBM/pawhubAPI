# Development Setup Guide

## Prerequisites

- Python 3.11+
- PostgreSQL 12+ with PostGIS extension
- pipenv (Python package manager)

## Local Development Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd pawhubAPI
```

### 2. Install Dependencies

```bash
# Install pipenv if not already installed
pip install pipenv

# Install project dependencies
pipenv install

# Install development dependencies (optional)
pipenv install --dev
```

### 3. Environment Setup

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/pawhub_db

# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Vultr Object Storage Configuration (Required for image uploads)
# Set to true to enable Vultr Object Storage
VULTR_OBJECT_STORAGE_ENABLED=true

# Your Vultr Object Storage credentials
# Get these from Vultr Customer Portal > Object Storage > S3 Credentials
VULTR_ACCESS_KEY_ID=your-vultr-access-key
VULTR_SECRET_ACCESS_KEY=your-vultr-secret-key

# Vultr Object Storage endpoint and region
# Examples:
# - For New Jersey (US East): https://ewr1.vultrobjects.com
# - For Seattle (US West): https://sjc1.vultrobjects.com
# - For Amsterdam (EU): https://ams1.vultrobjects.com
# - For Singapore (Asia): https://sgp1.vultrobjects.com
VULTR_ENDPOINT_URL=https://ewr1.vultrobjects.com

# Region must match the endpoint (examples: ewr1, sjc1, ams1, sgp1)
VULTR_REGION=ewr1

# Your bucket name (create this in Vultr Customer Portal)
VULTR_BUCKET_NAME=your-bucket-name

# File upload settings (optional)
# Maximum file size in bytes (default: 10MB)
MAX_FILE_SIZE=10485760
```

### 3.1. Vultr Object Storage Setup

Follow these steps to set up Vultr Object Storage:

1. **Create Vultr Account**: Sign up at [vultr.com](https://vultr.com)

2. **Create Object Storage Instance**:

   - Go to Vultr Customer Portal
   - Navigate to **Products** > **Cloud Storage** > **Object Storage**
   - Click **Deploy Now**
   - Choose your preferred region (closest to your users for better performance)
   - Select storage plan based on your needs

3. **Create a Bucket**:

   - Once the Object Storage instance is deployed, click on it
   - Go to **Buckets** section
   - Click **Add Bucket**
   - Enter a unique bucket name (this will be your `VULTR_BUCKET_NAME`)
   - **Important**: Set bucket permissions to allow public read access for uploaded images

4. **Get S3 Credentials**:

   - In your Object Storage instance, go to **Overview**
   - Find the **S3 Credentials** section
   - Note down:
     - **Hostname** (this is your `VULTR_ENDPOINT_URL`)
     - **Access Key** (this is your `VULTR_ACCESS_KEY_ID`)
     - **Secret Key** (this is your `VULTR_SECRET_ACCESS_KEY`)

5. **Configure CORS (Optional but Recommended)**:
   - If you plan to upload images from a web frontend, configure CORS
   - Go to **Advanced** > **CORS**
   - Add appropriate CORS rules for your domain

**Note**: Vultr Object Storage is S3-compatible, so it works seamlessly with boto3 and other S3 tools.

### 4. Database Setup

```bash
# Create PostgreSQL database
createdb pawhub_db

# Enable PostGIS extension
psql pawhub_db -c "CREATE EXTENSION postgis;"

# Activate virtual environment
pipenv shell

# Run migrations
python manage.py migrate

# Create superuser account
python manage.py createsuperuser
```

### 5. Start Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000` to verify the setup.

## Development Tools

### Django Extensions

The project includes `django-extensions` for additional management commands:

```bash
# Start enhanced shell with all models imported
python manage.py shell_plus

# Generate model graph (requires graphviz)
python manage.py graph_models -a -o models.png

# Show URLs
python manage.py show_urls
```

### Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test animals
python manage.py test users

# Run with coverage (if installed)
coverage run manage.py test
coverage report
```

### Database Management

```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (careful!)
python manage.py flush

# Load initial data (if fixtures exist)
python manage.py loaddata initial_data.json
```

## Code Style

### Patterns to Follow

1. **Custom APIViews**: Use custom APIView classes instead of ViewSets
2. **Custom Serializers**: Create custom serializer classes, not ModelSerializers
3. **Validation**: Use dedicated validator classes extending GeneralValidator
4. **Utils**: Extract business logic to utility functions
5. **Error Handling**: Use consistent error response format

### File Structure

```python
# Each app should have:
├── models.py          # Database models
├── serializers.py     # Custom serializer classes
├── views.py          # Custom APIView classes
├── urls.py           # URL patterns
├── validator.py      # Input validation classes
├── utils.py          # Business logic functions
└── tests.py          # Test cases
```

### Example Code Structure

```python
# validator.py
class CreateExampleInputValidator(GeneralValidator):
    def __init__(self, data) -> None:
        self.data = data

    def serialized_data(self):
        # Validation logic here
        pass

# utils.py
def create_example(data, user):
    # Business logic here
    pass

# views.py
class ExampleCreateAPI(APIView):
    authentication_classes = [UserTokenAuthentication]

    @swagger_auto_schema(...)
    def post(self, request):
        validated_data = CreateExampleInputValidator(
            request.data
        ).serialized_data()

        result = create_example(validated_data, request.user)
        return Response(result, status=status.HTTP_201_CREATED)
```

## Debugging

### Django Debug Toolbar (Development)

If installed, access debug information at `http://localhost:8000/__debug__/`

### Logging

Configure logging in `settings/django.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
```

### Common Issues

#### PostGIS Installation

On macOS:

```bash
brew install postgresql postgis
```

On Ubuntu:

```bash
sudo apt-get install postgresql postgresql-contrib postgis
```

#### Virtual Environment Issues

```bash
# Remove and recreate virtual environment
pipenv --rm
pipenv install
```

#### Migration Issues

```bash
# Reset migrations (development only)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete
python manage.py makemigrations
python manage.py migrate
```

## Performance Optimization

### Database Queries

- Use `select_related()` for ForeignKey relationships
- Use `prefetch_related()` for ManyToMany relationships
- Add database indexes for frequently queried fields
- Use `only()` and `defer()` for large models

### Caching

Configure Redis caching in production:

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## Git Workflow

### Branch Naming

- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `hotfix/critical-fix` - Critical production fixes

### Commit Messages

```
feat: add emergency reporting API
fix: resolve user registration validation
docs: update API documentation
test: add emergency creation tests
```

### Pre-commit Hooks

Consider adding:

- Black (code formatting)
- isort (import sorting)
- flake8 (linting)
- Django system checks

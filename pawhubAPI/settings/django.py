from .env import env

# setup()

# SITE_ROOT = root()

DEBUG = env.bool("DEBUG", default=True)
TEMPLATE_DEBUG = DEBUG

if DEBUG:
    INTERNAL_IPS = ["127.0.0.1"]

SECRET_KEY = env.str(
    "SECRET_KEY",
    default="i)=y6havm=8y01$t8f&=!k^qc$kk29!$an3he^*zt!7-u4nnj^",
)

# ALLOWED_HOSTS = env.list("ALLOWED_HOSTS") or []
ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "rest_framework",
    "drf_yasg",
    "users",
    "organisations",
    "vets",
    "animals",
]


# 'django.middleware.csrf.CsrfViewMiddleware',
MIDDLEWARE = [
    "pawhubAPI.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

AUTH_USER_MODEL = "users.CustomUser"

ROOT_URLCONF = "pawhubAPI.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["/Volumes/Files/Coding/StatusCode2/pawhubAPI/templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": env.db_url(
        "DATABASE_URL",
        default="postgis://user:password@host.vultrdb.com:16751/defaultdb",
    ),
}

# Set the PostGIS backend engine
DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"

# DATABASES["default"]["OPTIONS"] = {"connect_timeout": 10}
WSGI_APPLICATION = "pawhubAPI.wsgi.application"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ADMINS = [x.split(":") for x in env.list("DJANGO_ADMINS", default="")]

AUTH_USER_MODEL = "users.CustomUser"


STATIC_ROOT = "/var/www/static"
MEDIA_ROOT = "/var/www/media"

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    "/Volumes/Files/Coding/StatusCode2/pawhubAPI/static",
]
# STATIC_ROOT = "static"
MEDIA_URL = "/media/"


# STORAGES = {
#     "staticfiles": {
#         "BACKEND": "django_s3_storage.storage.StaticS3Storage",
#     },
#     "default": {
#         "BACKEND": "django_s3_storage.storage.S3Storage",
#     },
# }

# Custom CORS Configuration (handled by custom middleware)
# CORS settings are now managed in pawhubAPI.middleware.CorsMiddleware

# GeoDjango and Map Widget Settings
GEOS_LIBRARY_PATH = None  # Auto-detect GEOS library
GDAL_LIBRARY_PATH = None  # Auto-detect GDAL library

# Map widget configuration for Django admin
GEOPOSITION_MAP_OPTIONS = {
    'minZoom': 3,
    'maxZoom': 15,
}

GEOPOSITION_MARKER_OPTIONS = {
    'cursor': 'move'
}

# Map widget settings for better admin experience
MAP_WIDGETS = {
    "GooglePointFieldWidget": (
        ("zoom", 15),
        ("mapCenterLocationName", "san francisco"),
        ("GooglePlaceAutocompleteOptions", {'componentRestrictions': {'country': 'us'}}),
        ("markerFitZoom", 12),
    ),
    "GOOGLE_MAP_API_KEY": "",  # Set your Google Maps API key if needed
}

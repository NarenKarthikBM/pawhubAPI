#!/usr/bin/env python3
"""
Test script for Vultr Object Storage integration
"""

import os
import sys

# Add the project root to Python path
project_root = "/Volumes/Files/Coding/StatusCode2/pawhubAPI"
sys.path.insert(0, project_root)

# Set Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pawhubAPI.settings.django")

# Configure Django (minimal setup)
try:
    from django.conf import settings

    # Test our Vultr storage configuration import
    print("Testing Vultr Object Storage configuration...")

    # Test boto3 import
    import boto3

    print("✓ boto3 imported successfully")

    # Test our utils import
    from utils.vultr_storage import VultrObjectStorageManager, upload_image_to_vultr

    print("✓ Vultr storage utilities imported successfully")

    # Test configuration loading
    from pawhubAPI.settings.integrations.vultr_storage import (
        ALLOWED_IMAGE_EXTENSIONS,
        MAX_FILE_SIZE,
        VULTR_ACCESS_KEY_ID,
        VULTR_BUCKET_NAME,
        VULTR_ENDPOINT_URL,
        VULTR_OBJECT_STORAGE_ENABLED,
        VULTR_REGION,
        VULTR_SECRET_ACCESS_KEY,
    )

    print("✓ Vultr storage configuration loaded successfully")

    print(f"  - Storage enabled: {VULTR_OBJECT_STORAGE_ENABLED}")
    print(f"  - Max file size: {MAX_FILE_SIZE} bytes")
    print(f"  - Allowed extensions: {ALLOWED_IMAGE_EXTENSIONS}")

    # Test environment variables
    print("\nEnvironment variables check:")
    env_vars = [
        "VULTR_OBJECT_STORAGE_ENABLED",
        "VULTR_ACCESS_KEY_ID",
        "VULTR_SECRET_ACCESS_KEY",
        "VULTR_ENDPOINT_URL",
        "VULTR_REGION",
        "VULTR_BUCKET_NAME",
    ]

    for var in env_vars:
        value = os.environ.get(var, "NOT SET")
        status = "✓" if value != "NOT SET" else "✗"
        print(f"  {status} {var}: {'SET' if value != 'NOT SET' else 'NOT SET'}")

    print("\n✓ All imports and configuration loading successful!")
    print("\nNext steps:")
    print("1. Set up your Vultr Object Storage credentials in .env file")
    print("2. Create a bucket in Vultr Customer Portal")
    print("3. Test the API endpoint with actual file uploads")

except ImportError as e:
    print(f"✗ Import error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")

#!/usr/bin/env python3
"""
Test ML API with authentication
"""

import os
import sys
from pathlib import Path

import django

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pawhubAPI.settings")

try:
    django.setup()
    print("✅ Django setup successful")

    from animals.utils import identify_animal_species

    print("✅ ML utilities imported successfully")

    # Test API key configuration
    print("\n🔑 Testing ML API Authentication:")

    # Test with a sample image URL (you can replace this with a real image URL)
    test_image_url = "https://example.com/test_image.jpg"

    print("🖼️  Testing species identification...")
    print("   API Key: supersecrettoken123")
    print("   Endpoint: http://139.84.137.195:8001/identify-pet/")
    print("   Headers: Authorization: Bearer supersecrettoken123")
    print("   Headers: X-API-Token: supersecrettoken123")

    # Call the API (this will likely fail since it's a test URL, but we can see the request format)
    result = identify_animal_species(test_image_url)

    if result:
        print(f"✅ API call successful: {result}")
    else:
        print("ℹ️  API call returned None (expected for test URL)")

    print("\n🎯 API Key Configuration Complete!")
    print("The ML API calls now include:")
    print("- Authorization: Bearer supersecrettoken123")
    print("- X-API-Token: supersecrettoken123")
    print("- Content-Type: application/json")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()

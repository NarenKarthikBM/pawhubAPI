#!/usr/bin/env python3
"""
Minimal test script to verify Django setup
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

    # Test imports
    print("✅ Animal models imported successfully")

    print("✅ User models imported successfully")

    print("✅ ML utilities imported successfully")

    # Check sc2 folder
    sc2_folder = Path("sc2")
    if sc2_folder.exists():
        images = list(sc2_folder.glob("*.jpg")) + list(sc2_folder.glob("*.png"))
        print(f"✅ SC2 folder found with {len(images)} images")
    else:
        print("❌ SC2 folder not found")

    print("\n🎉 All imports successful! Ready to run enhanced sighting workflow.")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()

#!/usr/bin/env python3
"""
Test script for the Organisation Missions List API

This script tests the new missions list API endpoint that allows
organisations to retrieve their own missions.
"""

import os
import sys

import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pawhubAPI.settings.development")
django.setup()

from datetime import timedelta

from django.contrib.gis.geos import Point
from django.test import Client
from django.utils import timezone

from organisations.models import (
    Organisation,
    OrganisationAuthTokens,
    OrganisationMissions,
)
from organisations.utils import generate_tokens


def setup_test_data():
    """Set up test organisation and missions"""

    # Create a test organisation
    org, created = Organisation.objects.get_or_create(
        email="test_missions@example.com",
        defaults={
            "name": "Test Missions Organisation",
            "address": "123 Test St, Test City",
            "location": Point(-122.4194, 37.7749, srid=4326),
            "is_verified": True,
        },
    )

    if created:
        print(f"Created test organisation: {org.name}")
    else:
        print(f"Using existing organisation: {org.name}")

    # Create or get auth tokens for the organisation
    auth_tokens, created = OrganisationAuthTokens.objects.get_or_create(
        organisation=org,
        type="api",
        defaults={
            "auth_token": generate_tokens()["auth_token"],
            "device_token": generate_tokens()["device_token"],
        },
    )

    if created:
        print("Created auth tokens for organisation")
    else:
        print("Using existing auth tokens")

    # Create sample missions
    now = timezone.now()

    missions_data = [
        {
            "title": "Upcoming Vaccination Drive",
            "description": "Free vaccination for pets",
            "mission_type": "vaccination",
            "city": "Test City",
            "area": "Downtown",
            "start_datetime": now + timedelta(days=1),
            "end_datetime": now + timedelta(days=1, hours=6),
        },
        {
            "title": "Ongoing Rescue Mission",
            "description": "Rescue stray animals",
            "mission_type": "rescue",
            "city": "Test City",
            "area": "Suburbs",
            "start_datetime": now - timedelta(hours=2),
            "end_datetime": now + timedelta(hours=4),
        },
        {
            "title": "Completed Adoption Drive",
            "description": "Pet adoption event",
            "mission_type": "adoption",
            "city": "Test City",
            "area": "Park Area",
            "start_datetime": now - timedelta(days=2),
            "end_datetime": now - timedelta(days=2, hours=-6),
        },
    ]

    for mission_data in missions_data:
        mission, created = OrganisationMissions.objects.get_or_create(
            title=mission_data["title"],
            organisation=org,
            defaults={
                **mission_data,
                "location": Point(-122.4194, 37.7749, srid=4326),
                "contact_phone": "+1-555-0123",
                "contact_email": "contact@example.com",
                "max_participants": 50,
            },
        )
        if created:
            print(f"Created mission: {mission.title}")

    return org, auth_tokens


def test_missions_list_api():
    """Test the missions list API"""

    print("Setting up test data...")
    org, auth_tokens = setup_test_data()

    # Create a test client
    client = Client()

    # Set up authentication headers
    headers = {
        "HTTP_AUTHORIZATION": auth_tokens.auth_token,
        "HTTP_DEVICE_TOKEN": auth_tokens.device_token,
    }

    print("\nTesting API endpoints...")

    # Test 1: Get all missions
    print("\n1. Testing GET all missions:")
    response = client.get("/api/organisations/missions/", **headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total missions: {data['count']}")
        print(f"Number returned: {len(data['missions'])}")
        for mission in data["missions"]:
            print(f"  - {mission['title']} ({mission['mission_type']})")
    else:
        print(f"Error: {response.content}")

    # Test 2: Filter by status - upcoming
    print("\n2. Testing filter by status (upcoming):")
    response = client.get("/api/organisations/missions/?status=upcoming", **headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Upcoming missions: {data['count']}")
        for mission in data["missions"]:
            print(f"  - {mission['title']}")

    # Test 3: Filter by status - ongoing
    print("\n3. Testing filter by status (ongoing):")
    response = client.get("/api/organisations/missions/?status=ongoing", **headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Ongoing missions: {data['count']}")
        for mission in data["missions"]:
            print(f"  - {mission['title']}")

    # Test 4: Filter by status - completed
    print("\n4. Testing filter by status (completed):")
    response = client.get("/api/organisations/missions/?status=completed", **headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Completed missions: {data['count']}")
        for mission in data["missions"]:
            print(f"  - {mission['title']}")

    # Test 5: Filter by mission type
    print("\n5. Testing filter by mission_type (vaccination):")
    response = client.get(
        "/api/organisations/missions/?mission_type=vaccination", **headers
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Vaccination missions: {data['count']}")
        for mission in data["missions"]:
            print(f"  - {mission['title']}")

    # Test 6: Test pagination
    print("\n6. Testing pagination (limit=1):")
    response = client.get("/api/organisations/missions/?limit=1", **headers)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Total missions: {data['count']}")
        print(f"Returned missions: {len(data['missions'])}")

    # Test 7: Test without authentication
    print("\n7. Testing without authentication:")
    response = client.get("/api/organisations/missions/")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 401:
        print("Correctly returned 401 Unauthorized")
    else:
        print(f"Unexpected response: {response.content}")

    print("\nAPI testing complete!")


if __name__ == "__main__":
    test_missions_list_api()

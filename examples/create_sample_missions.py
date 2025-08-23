"""
Example usage and test data creation for Nearby Missions API

This script demonstrates how to create sample data and test the new API endpoint.
"""

from datetime import timedelta

from django.contrib.gis.geos import Point
from django.utils import timezone

from organisations.models import Organisation, OrganisationMissions


def create_sample_missions():
    """Create sample mission data for testing the nearby missions API"""

    # Create sample organisation
    org1, created = Organisation.objects.get_or_create(
        email="petcare@example.com",
        defaults={
            "name": "Pet Care Foundation",
            "address": "123 Main St, San Francisco, CA",
            "location": Point(-122.4194, 37.7749, srid=4326),  # San Francisco
            "is_verified": True,
        },
    )

    org2, created = Organisation.objects.get_or_create(
        email="animalrescue@example.com",
        defaults={
            "name": "Animal Rescue Society",
            "address": "456 Oak Ave, Oakland, CA",
            "location": Point(-122.2711, 37.8044, srid=4326),  # Oakland
            "is_verified": True,
        },
    )

    # Create upcoming missions
    now = timezone.now()

    # Mission 1: Vaccination drive (starting tomorrow)
    mission1, created = OrganisationMissions.objects.get_or_create(
        title="Free Pet Vaccination Drive",
        organisation=org1,
        defaults={
            "description": "Free vaccination for all pets in the Mission District area. Bring your pets and vaccination records.",
            "mission_type": "vaccination",
            "city": "San Francisco",
            "area": "Mission District",
            "location": Point(-122.4194, 37.7647, srid=4326),  # Mission District
            "start_datetime": now + timedelta(days=1, hours=10),  # Tomorrow at 10 AM
            "end_datetime": now + timedelta(days=1, hours=16),  # Tomorrow at 4 PM
            "is_active": True,
            "max_participants": 100,
            "contact_phone": "+1-555-0123",
            "contact_email": "vaccinations@petcare.org",
        },
    )

    # Mission 2: Adoption event (this weekend)
    mission2, created = OrganisationMissions.objects.get_or_create(
        title="Weekend Pet Adoption Fair",
        organisation=org2,
        defaults={
            "description": "Find your new best friend! Meet dozens of cats and dogs looking for loving homes.",
            "mission_type": "adoption",
            "city": "Oakland",
            "area": "Downtown Oakland",
            "location": Point(-122.2711, 37.8044, srid=4326),  # Oakland
            "start_datetime": now + timedelta(days=3, hours=9),  # This Saturday at 9 AM
            "end_datetime": now + timedelta(days=3, hours=17),  # This Saturday at 5 PM
            "is_active": True,
            "max_participants": 200,
            "contact_phone": "+1-555-0456",
            "contact_email": "adoptions@animalrescue.org",
        },
    )

    # Mission 3: Medical camp (next week)
    mission3, created = OrganisationMissions.objects.get_or_create(
        title="Free Animal Medical Camp",
        organisation=org1,
        defaults={
            "description": "Free basic medical checkups and treatments for stray and owned animals.",
            "mission_type": "medical",
            "city": "San Francisco",
            "area": "Castro District",
            "location": Point(-122.4350, 37.7609, srid=4326),  # Castro
            "start_datetime": now + timedelta(days=7, hours=8),  # Next week at 8 AM
            "end_datetime": now + timedelta(days=7, hours=15),  # Next week at 3 PM
            "is_active": True,
            "max_participants": 50,
            "contact_phone": "+1-555-0789",
            "contact_email": "medical@petcare.org",
        },
    )

    # Mission 4: Past mission (should not appear in results)
    mission4, created = OrganisationMissions.objects.get_or_create(
        title="Past Feeding Program",
        organisation=org2,
        defaults={
            "description": "This mission has already ended.",
            "mission_type": "feeding",
            "city": "San Francisco",
            "area": "SOMA",
            "location": Point(-122.4089, 37.7835, srid=4326),  # SOMA
            "start_datetime": now - timedelta(days=2),  # 2 days ago
            "end_datetime": now - timedelta(days=1),  # Yesterday
            "is_active": False,
            "max_participants": 30,
            "contact_phone": "+1-555-0999",
            "contact_email": "feeding@animalrescue.org",
        },
    )

    print("Sample missions created successfully!")
    print(
        f"Created missions: {mission1.title}, {mission2.title}, {mission3.title}, {mission4.title}"
    )
    print("\nTo test the API, use coordinates:")
    print("San Francisco: latitude=37.7749, longitude=-122.4194")
    print("Oakland: latitude=37.8044, longitude=-122.2711")


def test_api_usage_example():
    """Example of how to call the API programmatically"""

    print("\n" + "=" * 50)
    print("API Usage Example")
    print("=" * 50)

    # This would be used in actual client code
    api_call_example = """
# Example API call using requests library:

import requests

# Replace with actual user token
headers = {
    'Authorization': 'Token your_user_token_here',
    'Content-Type': 'application/json',
}

# Get missions near San Francisco
params = {
    'latitude': 37.7749,
    'longitude': -122.4194,
}

response = requests.get(
    'http://localhost:8000/api/organisations/missions/nearby/',
    headers=headers,
    params=params
)

if response.status_code == 200:
    missions = response.json()
    print(f"Found {len(missions)} nearby missions")
    for mission in missions:
        print(f"- {mission['title']} by {mission['organisation']['name']}")
else:
    print(f"Error: {response.status_code} - {response.text}")

# Filter by mission type
params['mission_type'] = 'vaccination'
response = requests.get(
    'http://localhost:8000/api/organisations/missions/nearby/',
    headers=headers,
    params=params
)
"""

    print(api_call_example)


if __name__ == "__main__":
    # To run this in Django shell:
    # python manage.py shell
    # exec(open('create_sample_missions.py').read())

    create_sample_missions()
    test_api_usage_example()

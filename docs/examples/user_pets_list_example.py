#!/usr/bin/env python3
"""
PawHub API - User Pets List Example

This script demonstrates how to use the User Pets List API endpoint
to retrieve a user's pets.

Requirements:
- Valid authentication token
- requests library (pip install requests)
"""

import requests


class PawHubUserPetsClient:
    """Client for interacting with PawHub User Pets API"""

    def __init__(self, base_url="http://localhost:8000", auth_token=None):
        """Initialize the client

        Args:
            base_url (str): Base URL of the PawHub API
            auth_token (str): User authentication token
        """
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.session = requests.Session()

        if auth_token:
            self.session.headers.update(
                {
                    "Authorization": f"Token {auth_token}",
                    "Content-Type": "application/json",
                }
            )

    def get_user_pets(self):
        """Get list of pets owned by the authenticated user

        Returns:
            dict: API response containing pets list and count
        """
        url = f"{self.base_url}/api/animals/pets/my-pets/"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}

    def display_pets(self, pets_data):
        """Display pets in a user-friendly format

        Args:
            pets_data (dict): Response from get_user_pets()
        """
        if pets_data.get("error"):
            print(f"❌ Error: {pets_data['error']}")
            return

        if not pets_data.get("success"):
            print("❌ Request was not successful")
            return

        pets = pets_data.get("pets", [])
        count = pets_data.get("count", 0)

        print(f"🐾 Found {count} pet(s):\n")

        if count == 0:
            print("   No pets registered yet.")
            return

        for i, pet in enumerate(pets, 1):
            print(f"{i}. 🐕 {pet['name']}")
            print(f"   Species: {pet['species']}")
            print(f"   Breed: {pet['breed']}")
            print(f"   Sterilized: {'✅ Yes' if pet['is_sterilized'] else '❌ No'}")

            # Display images
            images = pet.get("images", [])
            if images:
                print(f"   Images: {len(images)} photo(s)")
                for img in images[:2]:  # Show first 2 images
                    print(f"     📸 {img['image_url']}")
                if len(images) > 2:
                    print(f"     ... and {len(images) - 2} more")
            else:
                print("   Images: No photos yet")

            # Display location
            location = pet.get("location")
            if location:
                print(
                    f"   Location: {location['latitude']:.4f}, {location['longitude']:.4f}"
                )
            else:
                print("   Location: Not set")

            print(f"   Registered: {pet['created_at'][:10]}")
            print()


def main():
    """Main example function"""

    # Example usage - replace with your actual token
    AUTH_TOKEN = "your_auth_token_here"  # Replace with actual token
    BASE_URL = "http://localhost:8000"  # Replace with actual API URL

    # Initialize client
    client = PawHubUserPetsClient(BASE_URL, AUTH_TOKEN)

    print("🐾 PawHub - User Pets List Example")
    print("=" * 40)

    # Get user's pets
    print("📡 Fetching your pets...")
    pets_data = client.get_user_pets()

    # Display results
    client.display_pets(pets_data)

    # Example of using the raw data
    if pets_data.get("success"):
        pets = pets_data["pets"]

        # Group by species
        species_count = {}
        for pet in pets:
            species = pet["species"]
            species_count[species] = species_count.get(species, 0) + 1

        if species_count:
            print("📊 Summary by Species:")
            for species, count in species_count.items():
                print(f"   {species}: {count} pet(s)")


def example_with_error_handling():
    """Example with comprehensive error handling"""

    client = PawHubUserPetsClient("http://localhost:8000", "invalid_token")

    try:
        result = client.get_user_pets()

        if result.get("error"):
            print(f"API Error: {result['error']}")
        elif result.get("success"):
            print(f"Success! Found {result['count']} pets.")
        else:
            print("Unexpected response format")

    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    print("Choose an example to run:")
    print("1. Main example (requires valid token)")
    print("2. Error handling example")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        main()
    elif choice == "2":
        example_with_error_handling()
    else:
        print("Invalid choice")

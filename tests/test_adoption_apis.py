#!/usr/bin/env python3
"""
Test script for the new adoption APIs

This script tests:
1. Organization adoption listings API
2. Mark adoption as adopted API

To run this test:
python test_adoption_apis.py
"""

import sys

import requests

# Configuration
BASE_URL = "http://localhost:8000"
ORGANISATION_AUTH_TOKEN = "your-organisation-auth-token-here"
ORGANISATION_DEVICE_TOKEN = "your-organisation-device-token-here"

# Headers for organisation authentication
headers = {
    "Authorization": ORGANISATION_AUTH_TOKEN,
    "Device-Token": ORGANISATION_DEVICE_TOKEN,
    "Content-Type": "application/json",
}


def test_organisation_adoptions_list():
    """Test the organisation adoptions list API"""
    print("🧪 Testing Organisation Adoptions List API...")

    url = f"{BASE_URL}/animals/adoptions/my-listings/"

    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Found {data.get('count', 0)} adoption listings")
            print(
                f"Organisation: {data.get('organisation', {}).get('name', 'Unknown')}"
            )

            # Display first few adoptions
            adoptions = data.get("adoptions", [])
            for i, adoption in enumerate(adoptions[:3]):
                print(
                    f"  Adoption {i+1}: {adoption['profile']['name']} ({adoption['profile']['species']}) - Status: {adoption['status']}"
                )

        elif response.status_code == 401:
            print("❌ Authentication failed. Please check your auth tokens.")
        else:
            print(f"❌ Error: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")


def test_mark_adoption_as_adopted():
    """Test the mark adoption as adopted API"""
    print("\n🧪 Testing Mark Adoption as Adopted API...")

    # First, get the list of adoptions to find one to mark as adopted
    list_url = f"{BASE_URL}/animals/adoptions/my-listings/"

    try:
        response = requests.get(list_url, headers=headers)

        if response.status_code != 200:
            print("❌ Could not fetch adoption list to test marking as adopted")
            return

        data = response.json()
        adoptions = data.get("adoptions", [])

        # Find an available adoption to mark as adopted
        available_adoption = None
        for adoption in adoptions:
            if adoption["status"] == "available":
                available_adoption = adoption
                break

        if not available_adoption:
            print("ℹ️  No available adoptions found to mark as adopted")
            return

        # Mark the adoption as adopted
        mark_url = f"{BASE_URL}/animals/adoptions/mark-adopted/"
        mark_data = {"adoption_id": available_adoption["id"]}

        response = requests.patch(mark_url, headers=headers, json=mark_data)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Marked adoption as adopted")
            print(f"Pet: {result['adoption']['profile']['name']}")
            print(f"New status: {result['adoption']['status']}")
        elif response.status_code == 400:
            print(f"❌ Bad request: {response.text}")
        elif response.status_code == 404:
            print(f"❌ Adoption not found or no permission: {response.text}")
        else:
            print(f"❌ Error: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")


def test_mark_already_adopted():
    """Test marking an already adopted adoption (should fail)"""
    print("\n🧪 Testing Mark Already Adopted Adoption (Should Fail)...")

    # First, get the list of adoptions to find an already adopted one
    list_url = f"{BASE_URL}/animals/adoptions/my-listings/"

    try:
        response = requests.get(list_url, headers=headers)

        if response.status_code != 200:
            print("❌ Could not fetch adoption list")
            return

        data = response.json()
        adoptions = data.get("adoptions", [])

        # Find an already adopted adoption
        adopted_adoption = None
        for adoption in adoptions:
            if adoption["status"] == "adopted":
                adopted_adoption = adoption
                break

        if not adopted_adoption:
            print("ℹ️  No adopted adoptions found to test with")
            return

        # Try to mark the already adopted adoption as adopted again
        mark_url = f"{BASE_URL}/animals/adoptions/mark-adopted/"
        mark_data = {"adoption_id": adopted_adoption["id"]}

        response = requests.patch(mark_url, headers=headers, json=mark_data)

        if response.status_code == 500 and "already marked as adopted" in response.text:
            print("✅ Correctly handled already adopted case")
        else:
            print(f"❌ Unexpected response: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")


def main():
    """Run all tests"""
    print("🚀 Starting Adoption APIs Test Suite")
    print("=" * 50)

    if ORGANISATION_AUTH_TOKEN == "your-organisation-auth-token-here":
        print(
            "⚠️  Please update the ORGANISATION_AUTH_TOKEN and ORGANISATION_DEVICE_TOKEN variables"
        )
        print("   You can get these by registering/logging in as an organisation")
        sys.exit(1)

    test_organisation_adoptions_list()
    test_mark_adoption_as_adopted()
    test_mark_already_adopted()

    print("\n" + "=" * 50)
    print("🏁 Test Suite Complete")


if __name__ == "__main__":
    main()

# Breed Analysis Feature Implementation

## Overview

This implementation adds breed analysis functionality to the animal sighting system, allowing the ML model to provide unique breed-related features that are then used to improve the similarity matching process.

## Changes Made

### 1. Database Model Updates

#### AnimalSighting Model (`animals/models.py`)

- Added `breed_analysis` field (JSONField) to store unique features from ML analysis
- Field allows null/blank values and defaults to an empty list

#### AnimalProfileModel Model (`animals/models.py`)

- Added `breed_analysis` field (JSONField) to store breed features for animal profiles
- This allows profiles to also store breed analysis data for matching

### 2. ML API Integration Updates

#### Updated ML API Endpoint (`animals/utils.py`)

- Changed from `identify-pet` to `identify-species` endpoint
- Updated function name from `identify_pet_species()` to `identify_animal_species()`
- The new endpoint should return a response that includes `breed_analysis` field

#### New Breed Similarity Function (`animals/utils.py`)

- Added `calculate_breed_similarity()` function that calculates Jaccard similarity between breed feature arrays
- Uses intersection over union formula: `intersection_size / union_size`
- Returns score between 0.0 (no similarity) and 1.0 (perfect match)

### 3. Enhanced Similarity Matching

#### Updated `find_similar_animal_profiles()` function (`animals/utils.py`)

- Now accepts optional `breed_analysis` parameter
- Combines image similarity (70% weight) with breed similarity (30% weight)
- Returns additional metadata including separate image and breed similarity scores
- Formula: `combined_score = 0.7 * image_similarity + 0.3 * breed_similarity`

### 4. Sighting Creation Workflow Updates

#### CreateSightingAPI (`animals/views.py`)

- Extracts `breed_analysis` from ML API response
- Passes breed analysis to sighting creation and similarity matching functions

#### Updated Utility Functions (`animals/utils.py`)

- `create_sighting_record()` now accepts and stores breed analysis
- `create_stray_animal_profile()` now accepts and stores breed analysis
- `SightingSelectProfileAPI` passes breed analysis from sighting to new profiles

### 5. Serializer Updates

#### AnimalProfileModelSerializer (`animals/serializers.py`)

- Added `breed_analysis` field to the details serializer output
- Uses safe attribute access with fallback to empty list

#### AnimalSightingSerializer (`animals/serializers.py`)

- Added `breed_analysis` field to the details serializer output
- Uses safe attribute access with fallback to empty list

### 6. Database Migration

#### Migration File: `0006_add_breed_analysis.py`

- Adds `breed_analysis` JSONField to both `AnimalSighting` and `AnimalProfileModel` tables
- Fields are nullable and default to empty lists

## API Response Format

### Updated Sighting Response

```json
{
  "sighting": {
    "id": 1,
    "breed_analysis": ["fluffy_coat", "pointed_ears", "long_tail"],
    "location": {...},
    "image": {...},
    "reporter": {...},
    "created_at": "..."
  },
  "ml_species_identification": {
    "species": "dog",
    "breed": "Golden Retriever",
    "breed_analysis": ["fluffy_coat", "pointed_ears", "long_tail"],
    "confidence": 0.95
  },
  "matching_profiles": [
    {
      "profile": {...},
      "similarity_score": 0.85,
      "image_similarity": 0.9,
      "breed_similarity": 0.7,
      "distance_km": 2.5,
      "matching_image_url": "..."
    }
  ]
}
```

### Updated Profile Response

```json
{
  "id": 1,
  "name": "Buddy",
  "species": "dog",
  "breed": "Golden Retriever",
  "breed_analysis": ["fluffy_coat", "pointed_ears", "long_tail"],
  "type": "pet",
  "location": {...},
  "images": [...],
  "owner": {...}
}
```

## ML API Requirements

The ML model's `/identify-species` endpoint should return a response in this format:

```json
{
  "species": "dog",
  "breed": "Golden Retriever",
  "confidence": 0.95,
  "breed_analysis": ["fluffy_coat", "pointed_ears", "long_tail", "golden_color", "medium_size"]
}
```

## Benefits

1. **Improved Matching Accuracy**: Combines visual similarity with breed-specific features
2. **Better False Positive Reduction**: Different breeds with similar appearance can be distinguished
3. **Enhanced User Experience**: More accurate matching leads to better sighting correlations
4. **Scalable Feature Set**: Easy to add new breed features as the ML model improves

## Usage Example

When a user uploads a sighting:

1. Image is processed by ML API to get species identification and breed analysis
2. Breed analysis features are stored in the sighting record
3. Similarity matching considers both image vectors and breed features
4. Results are ranked by combined similarity score
5. Users see more accurate matches with detailed similarity breakdowns

This implementation provides a robust foundation for incorporating breed-specific features into the animal matching system while maintaining backward compatibility with existing functionality.

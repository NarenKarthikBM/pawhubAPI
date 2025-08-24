# Enhanced Mock Data Creation - SC2 Sighting Workflow

## Overview

The enhanced mock data script now implements a sophisticated ML-powered sighting workflow that mimics real-world animal monitoring scenarios. This system creates realistic sightings with similarity matching, geographic clustering around Kolkata, and temporal distribution over the past month.

## Key Features

### 🎯 ML-Enhanced Similarity Matching

- **90% similarity threshold** for animal matching
- **Vector embeddings** for image similarity comparison
- **Breed analysis** for characteristic matching
- **Combined scoring** (70% image + 30% breed features)

### 📍 Geographic Distribution

- **Center location**: Kolkata, India (22.96391456958128, 88.53245371532486)
- **Search radius**: 20km from center point
- **Uniform distribution**: Proper circular distribution algorithm
- **Realistic clustering**: Animals sighted in believable patterns

### ⏰ Temporal Distribution

- **Time range**: Past 30 days from current date
- **Random scatter**: Realistic distribution over time period
- **Historical data**: All sightings have past timestamps

### 🔬 ML Processing Pipeline

1. **Image Upload**: Process images from `sc2/` folder
2. **Species Detection**: ML API identifies species and breed
3. **Feature Extraction**: Generate breed analysis characteristics
4. **Vector Generation**: Create 1536-dimension embeddings
5. **Similarity Search**: Find matching animals within radius
6. **Decision Logic**: Match existing or create new profile

## Usage

### Command Line

```bash
# Basic usage - looks for sc2/ folder in current directory
python create_mock_data_simple.py

# Specify images folder - will look for sc2/ subfolder within it
python create_mock_data_simple.py /path/to/images
# This will use: /path/to/images/sc2/
```

### Folder Structure Required

```
your_images_folder/
└── sc2/
    ├── animal1.jpg
    ├── stray_dog.png
    ├── cat_sighting.jpeg
    └── ...
```

## Workflow Details

### Step 1: Image Processing

- Load all images from `sc2/` folder
- Support formats: `.jpg`, `.jpeg`, `.png`, `.webp`
- Upload to Vultr storage via ML API
- Extract species, breed, and visual features

### Step 2: Similarity Analysis

For each processed image:

1. **Geographic Filter**: Find animals within 20km of sighting location
2. **Vector Comparison**: Calculate cosine similarity of embeddings
3. **Breed Matching**: Compare visual characteristics
4. **Combined Score**: Weighted combination of similarity metrics
5. **Threshold Check**: Only match if >90% similar

### Step 3: Animal Profile Management

**If match found (>90% similarity)**:

- Add sighting to existing animal profile
- Link new image as additional evidence
- Update animal's sighting history

**If no match found**:

- Create new animal profile with ML-detected data
- Set species, breed, and characteristics from ML analysis
- Create initial media record with embedding

### Step 4: Sighting Record Creation

- **Location**: Random point within 20km of Kolkata
- **Time**: Random datetime within past 30 days
- **Reporter**: Random user from created test users
- **Evidence**: Processed image with ML data
- **Analysis**: Breed features and embeddings

## Expected Output

### Console Logging

```
🔍 Creating 50 enhanced sightings with similarity matching...
📁 Found 23 images in SC2 folder

🖼️  Processing sighting #1: dog_golden.jpg
🔬 ML detected: Dog - Golden Retriever
📊 Features extracted: 8 characteristics
✅ Found matching animal: Buddy (similarity: 94.2%)
✅ Created sighting #1 for Buddy

🖼️  Processing sighting #2: cat_stray.jpg
🔬 ML detected: Cat - Domestic Shorthair
📊 Features extracted: 6 characteristics
🆕 No similar animals found (>90% threshold), creating new profile...
🐾 Created new animal profile: Spotted Cat #2
✅ Created sighting #2 for Spotted Cat #2
```

### Data Statistics

- **Geographic spread**: All sightings within 20km radius
- **Temporal spread**: Distributed over 30-day period
- **Animal profiles**: Mix of matched and newly created
- **Similarity accuracy**: Only high-confidence matches (>90%)
- **ML processing**: Real species/breed detection

## Benefits

### For Testing

- **Realistic data**: Mimics actual community monitoring
- **Edge cases**: Tests both matching and creation workflows
- **Performance**: Tests ML API integration under load
- **Geographic**: Tests location-based queries and indexing

### For Development

- **Similarity algorithms**: Validates matching logic
- **ML integration**: Tests API error handling
- **Database performance**: Tests with realistic query patterns
- **User experience**: Provides realistic demo data

## Technical Implementation

### Similarity Calculation

```python
# Combined similarity score
combined_similarity = (
    0.7 * image_similarity_score +
    0.3 * breed_similarity_score
)

# Only match if above threshold
if combined_similarity >= 0.9:
    # Add sighting to existing animal
else:
    # Create new animal profile
```

### Geographic Distribution

```python
# Proper circular distribution
angle = random.uniform(0, 2 * math.pi)
radius_km = 20 * math.sqrt(random.uniform(0, 1))

# Convert to lat/lng offsets
lat_offset = radius_km * lat_per_km * math.sin(angle)
lng_offset = radius_km * lng_per_km * math.cos(angle)
```

### Temporal Distribution

```python
# Random time within past month
now = timezone.now()
one_month_ago = now - timedelta(days=30)
random_time = one_month_ago + timedelta(
    seconds=random.randint(0, int(time_diff.total_seconds()))
)
```

## Integration Points

### With Production APIs

- Uses same `upload_and_process_image()` function
- Uses same `find_similar_profiles()` logic
- Uses same similarity thresholds and weights
- Uses same vector embedding system

### With Database Models

- Creates `AnimalProfileModel` instances with ML data
- Creates `AnimalSighting` records with proper timestamps
- Creates `AnimalMedia` with embeddings and URLs
- Maintains referential integrity

This enhanced workflow provides comprehensive testing data that closely mirrors real-world usage patterns and validates the entire ML-powered sighting pipeline.

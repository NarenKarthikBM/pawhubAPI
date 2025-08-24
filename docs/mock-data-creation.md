# Mock Data Creation Scripts for PawHub API

This folder contains scripts to generate realistic mock data for the PawHub API, including stray animal profiles, sightings, emergencies, and adoption listings. **The scripts now integrate with the ML workflow to automatically detect species and breeds from animal images.**

## 🤖 ML Integration Features

### Automatic Species & Breed Detection

- **Uses the same ML workflow** as the production sighting system
- **Processes images through ML APIs** at `http://139.84.137.195:8001`
- **Extracts species, breed, and breed analysis** from uploaded images
- **Generates vector embeddings** for similarity matching
- **Falls back gracefully** to random data if ML APIs are unavailable

### Realistic Data Generation

- **Species detection**: Automatically identifies if image contains dog, cat, etc.
- **Breed analysis**: Extracts visual features like coat type, ear shape, size
- **Vector embeddings**: Creates embeddings for similarity search testing
- **Image processing**: Uploads to Vultr storage with full ML pipeline

## Scripts Available

### 1. Django Management Command: `create_mock_data.py`

**Location**: `animals/management/commands/create_mock_data.py`

This is a Django management command that creates comprehensive mock data with all features.

#### Usage:

```bash
# Basic usage (creates default amounts of data)
python manage.py create_mock_data --images-folder /path/to/your/images

# Customize the number of records created
python manage.py create_mock_data \
    --images-folder /path/to/your/images \
    --num-animals 30 \
    --num-sightings 50 \
    --num-emergencies 15 \
    --num-lost 10 \
    --num-adoptions 20
```

#### Parameters:

- `--images-folder`: Path to folder containing animal images (required)
- `--num-animals`: Number of stray animals to create (default: 50)
- `--num-sightings`: Number of sightings to create (default: 100)
- `--num-emergencies`: Number of emergencies to create (default: 20)
- `--num-lost`: Number of lost pets to create (default: 15)
- `--num-adoptions`: Number of adoption listings to create (default: 30)

### 2. Simple Script: `create_mock_data_simple.py`

**Location**: `create_mock_data_simple.py` (project root)

A standalone script that's easier to run and customize for basic testing.

#### Usage:

```bash
# With images folder
python create_mock_data_simple.py /path/to/your/images

# Without images (uses placeholders)
python create_mock_data_simple.py
```

#### What it creates:

- 5 mock users with test accounts
- 2 mock organizations
- 20 stray animal profiles **with ML-detected species and breeds**
- 30 animal sightings **with ML-processed images and breed analysis**
- 10 emergency reports **with ML-processed evidence images**
- 15 adoption listings **with ML-analyzed animal profiles**

## 🎯 ML Workflow Integration

### How It Works

1. **Image Upload**: Each image is uploaded to Vultr Object Storage
2. **ML Processing**: Images are processed through the same ML APIs used in production:
   - `identify-pet` endpoint for species/breed detection
   - `generate-embedding` endpoint for vector embeddings
3. **Data Extraction**: Species, breed, and visual features are extracted from ML results
4. **Profile Creation**: Animal profiles are created using ML-detected data
5. **Fallback**: If ML fails, scripts use realistic fallback data

### ML API Integration

```python
# Example of ML processing in the scripts
image_url, species_data, embedding = upload_and_process_image(uploaded_file)

if species_data:
    species = species_data.get('species')  # e.g., "Dog"
    breed = species_data.get('breed')      # e.g., "Golden Retriever"
    breed_analysis = species_data.get('breed_analysis')  # Visual features
```

### Console Output

```bash
ML detected: Dog - Golden Retriever for Buddy #1
ML detected: Cat - Siamese for Luna #2
Using fallback data: Dog - Mixed Breed for Max #3  # When ML fails
Sighting #1: ML detected 4 features
Emergency #1: ML detected Dog
```

## Image Requirements

### Supported Formats

- `.jpg`, `.jpeg`, `.png`, `.webp`

### Image Organization

Place all animal images in a single folder. The scripts will randomly select images for each animal profile and sighting.

### Example Image Folder Structure

```
/your/images/folder/
├── dog1.jpg
├── cat1.png
├── dog2.jpeg
├── rabbit1.jpg
├── stray_cat.png
└── ...
```

## Data Created

### User Accounts

- **Emails**: john.doe@example.com, jane.smith@example.com, etc.
- **Password**: `testpassword123` (for all test users)
- **Username**: Based on names (johndoe, janesmith, etc.)

### Organizations

- **City Animal Rescue** (info@cityrescue.org)
- **Stray Care Foundation** (contact@straycare.org)
- **Animal Welfare Society** (help@animalwelfare.org)

### Animal Profiles

- **Species**: Dogs, Cats, Rabbits, Birds **detected by ML models**
- **Types**: Stray animals (for sightings) and pets (for lost reports)
- **Locations**: Random coordinates around major US cities
- **Breed Analysis**: **ML-extracted visual features** like coat type, ear shape, size
- **Vector Embeddings**: **Generated by ML models** for similarity matching

### Sightings

- **Random locations** around major cities
- **Reporter assignments** from created users
- **Images** processed through **full ML pipeline**
- **Breed analysis data** extracted from **ML vision models**
- **Vector embeddings** for similarity search testing

### Emergencies

- **Types**: injury, rescue_needed, aggressive_behavior, missing_lost_pet
- **Status**: active or resolved
- **Evidence images** processed through **ML APIs**
- **Species detection** logged for each emergency

### Adoption Listings

- **Posted by organizations**
- **Animal profiles with ML-detected species/breeds**
- **Multiple images per animal** with embeddings
- **Status**: available or adopted

## Image Upload Integration

### Vultr Storage

If `utils.vultr_storage.upload_to_vultr` is available, images will be uploaded to Vultr storage automatically.

### Fallback

If Vultr upload fails or is unavailable, the scripts use placeholder URLs or local paths.

## Prerequisites

### Environment Setup

```bash
# Make sure Django environment is configured
export DJANGO_SETTINGS_MODULE=pawhubAPI.settings.local

# Install dependencies
pipenv install

# Activate virtual environment
pipenv shell

# Run migrations first
python manage.py migrate
```

### Database Requirements

- PostgreSQL with PostGIS extension
- All migrations applied
- Geographic indexing configured

## Customization

### Adding More Species/Breeds

Edit the `species_choices` and `breed_choices` dictionaries in either script:

```python
species_choices = ['Dog', 'Cat', 'Rabbit', 'Bird', 'Hamster', 'Guinea Pig']
breed_choices = {
    'Dog': ['Labrador', 'German Shepherd', 'Custom Breed'],
    # Add more species and breeds
}
```

### Modifying Locations

Change the `city_centers` list in `get_random_location()` to use different geographic areas:

```python
city_centers = [
    (-74.0060, 40.7128),  # New York
    (-118.2437, 34.0522), # Los Angeles
    # Add your preferred coordinates
]
```

### Custom Names

Modify the name lists for animals:

```python
stray_names = ['Your', 'Custom', 'Names', 'Here']
adoption_names = ['Hope', 'Lucky', 'Custom', 'Names']
```

## Troubleshooting

### Images Not Loading

- Check image folder path is correct
- Ensure images are in supported formats
- Verify folder permissions

### Geographic Data Issues

- Ensure PostGIS is installed and configured
- Check that geographic indexes are created
- Verify SRID 4326 is supported

### Import Errors

- Make sure Django is properly configured
- Check that all migrations are applied
- Verify virtual environment is activated

### Memory Issues with Large Datasets

- Reduce the number of items created
- Process in smaller batches
- Monitor database performance

## Security Notes

- Mock users have weak passwords (`testpassword123`)
- **Never use in production**
- Delete mock data before deploying
- Organizations are created without verification

## Example Usage Workflow

```bash
# 1. Prepare images
mkdir /tmp/animal_images
# Copy your animal images to this folder

# 2. Run the simple script for basic testing
python create_mock_data_simple.py /tmp/animal_images

# 3. Or use the management command for comprehensive data
python manage.py create_mock_data \
    --images-folder /tmp/animal_images \
    --num-animals 100 \
    --num-sightings 200

# 4. Verify data in Django admin or API endpoints
python manage.py runserver
# Visit http://localhost:8000/admin
```

This will create a realistic dataset for testing all the animal-related features of the PawHub API.

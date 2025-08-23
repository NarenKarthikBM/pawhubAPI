# Vultr Object Storage Setup Guide

This guide will walk you through setting up Vultr Object Storage for the PawHub API to handle image uploads for animal sightings.

## Overview

The PawHub API has been updated to upload images directly to Vultr Object Storage instead of accepting image URLs. This provides:

- **Security**: No exposure of internal file systems
- **Scalability**: Cloud-based storage that scales automatically
- **Performance**: CDN-like access to images globally
- **Cost-effectiveness**: Pay only for what you use

## Prerequisites

- Vultr account (sign up at [vultr.com](https://vultr.com))
- Python environment with boto3 installed
- Django project set up with the updated code

## Step-by-Step Setup

### 1. Create Vultr Object Storage

1. **Log into Vultr Customer Portal**

   - Go to [my.vultr.com](https://my.vultr.com)
   - Navigate to **Products** → **Cloud Storage** → **Object Storage**

2. **Deploy Object Storage Instance**

   - Click **Deploy Now**
   - Choose a region close to your users:
     - `ewr1` - New Jersey (US East)
     - `sjc1` - Seattle (US West)
     - `ams1` - Amsterdam (EU)
     - `sgp1` - Singapore (Asia)
   - Select storage plan (start with 1TB for development)
   - Click **Deploy Now**

3. **Wait for Deployment**
   - Instance will be ready in a few minutes
   - You'll receive an email confirmation

### 2. Create Storage Bucket

1. **Access Your Object Storage**

   - Click on your deployed Object Storage instance
   - Go to the **Buckets** section

2. **Create New Bucket**
   - Click **Add Bucket**
   - Enter a unique bucket name (e.g., `pawhub-images-prod`)
   - **Important**: Make the bucket publicly readable
   - Click **Create Bucket**

### 3. Get S3 Credentials

1. **Navigate to Overview**

   - In your Object Storage instance, click **Overview**
   - Find the **S3 Credentials** section

2. **Note Down Credentials**
   - **Hostname**: This is your endpoint URL (e.g., `https://ewr1.vultrobjects.com`)
   - **Access Key**: Your access key ID
   - **Secret Key**: Your secret access key

### 4. Configure Environment Variables

Create or update your `.env` file:

```bash
# Vultr Object Storage Configuration
VULTR_OBJECT_STORAGE_ENABLED=true

# Credentials from Vultr Customer Portal
VULTR_ACCESS_KEY_ID=your_access_key_here
VULTR_SECRET_ACCESS_KEY=your_secret_key_here

# Endpoint and region (must match your Object Storage location)
VULTR_ENDPOINT_URL=https://ewr1.vultrobjects.com
VULTR_REGION=ewr1

# Your bucket name
VULTR_BUCKET_NAME=pawhub-images-prod

# Optional: File upload limits
MAX_FILE_SIZE=10485760  # 10MB in bytes
```

### 5. Install Dependencies

Ensure boto3 is installed:

```bash
# Using pip
pip install boto3

# Or using pipenv
pipenv install boto3
```

### 6. Test Configuration

Run the test script:

```bash
python3 test_vultr_integration.py
```

You should see:

```
✓ boto3 imported successfully
✓ Vultr storage utilities imported successfully
✓ Vultr storage configuration loaded successfully
✓ All imports and configuration loading successful!
```

### 7. Verify Bucket Permissions

**Important**: Ensure your bucket allows public read access for uploaded images:

1. Go to your bucket in Vultr Customer Portal
2. Check **Permissions** settings
3. Enable public read access for objects

### 8. Optional: Configure CORS

If you plan to upload directly from a web frontend:

1. Go to **Advanced** → **CORS** in your Object Storage
2. Add CORS rules for your domain:

```json
{
  "CORSRules": [
    {
      "AllowedOrigins": ["https://yourdomain.com"],
      "AllowedMethods": ["GET", "POST", "PUT"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3000
    }
  ]
}
```

## Testing the API

### Using curl

```bash
curl -X POST http://localhost:8000/api/animals/sightings/ \
  -H "Authorization: Token your_auth_token" \
  -F "image_file=@/path/to/image.jpg" \
  -F "longitude=-122.4194" \
  -F "latitude=37.7749"
```

### Using Python requests

```python
import requests

url = "http://localhost:8000/api/animals/sightings/"
headers = {"Authorization": "Token your_auth_token"}
data = {
    "longitude": -122.4194,
    "latitude": 37.7749
}

with open('image.jpg', 'rb') as f:
    files = {'image_file': f}
    response = requests.post(url, data=data, files=files, headers=headers)
    print(response.json())
```

## Troubleshooting

### Common Issues

**1. Import Error: "boto3 could not be resolved"**

- Solution: Install boto3 with `pip install boto3`

**2. "Access denied to Vultr Object Storage"**

- Check your access key and secret key
- Verify the bucket name is correct
- Ensure bucket allows public writes

**3. "Bucket does not exist"**

- Verify bucket name in environment variables
- Check that bucket was created in the same region as your endpoint

**4. "Failed to process image"**

- Ensure the uploaded file is a valid image
- Check file size limits (default 10MB)
- Verify allowed file extensions

### Getting Help

- Check Vultr documentation: [docs.vultr.com](https://docs.vultr.com)
- Review server logs for detailed error messages
- Test with the provided test script

## Security Considerations

1. **Never commit credentials to version control**
2. **Use environment variables for all sensitive data**
3. **Regularly rotate access keys**
4. **Monitor storage usage and costs**
5. **Consider implementing virus scanning for uploads**

## Cost Optimization

- Monitor storage usage in Vultr dashboard
- Set up alerts for unusual usage patterns
- Consider lifecycle policies for old images
- Use appropriate storage class for your use case

## Next Steps

Once set up, you can:

1. Test the sighting creation API with file uploads
2. Monitor storage usage in Vultr dashboard
3. Set up automated backups if needed
4. Implement image optimization for better performance

"""
Vultr Object Storage utilities for file upload and management
"""

import mimetypes
import uuid
from typing import Tuple

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from django.conf import settings


class VultrObjectStorageManager:
    """Manager class for Vultr Object Storage operations"""

    def __init__(self):
        self.enabled = True
        if not self.enabled:
            raise ValueError("Vultr Object Storage is not enabled")

        self.access_key_id = getattr(settings, "VULTR_ACCESS_KEY_ID", "3XBPP2V081DPDI0KM5MC")
        self.secret_access_key = getattr(settings, "VULTR_SECRET_ACCESS_KEY", "yWmDm5mELAI7kfnYDawDEkxh5wJaJfG3z5mAACrW")
        self.endpoint_url = getattr(settings, "VULTR_ENDPOINT_URL", "https://blr1.vultrobjects.com")
        self.region = getattr(settings, "VULTR_REGION", "blr1")
        self.bucket_name = getattr(settings, "VULTR_BUCKET_NAME", "pawhub-bucket")

        if not all(
            [
                self.access_key_id,
                self.secret_access_key,
                self.endpoint_url,
                self.bucket_name,
            ]
        ):
            raise ValueError("Missing required Vultr Object Storage configuration")

        self._client = None

    @property
    def client(self):
        """Lazy initialization of S3 client"""
        if self._client is None:
            self._client = boto3.client(
                "s3",
                aws_access_key_id=self.access_key_id,
                aws_secret_access_key=self.secret_access_key,
                endpoint_url=self.endpoint_url,
                region_name=self.region,
            )
        return self._client

    def validate_file(self, file) -> Tuple[bool, str]:
        """
        Validate uploaded file

        Args:
            file: Django uploaded file object

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        max_size = getattr(settings, "MAX_FILE_SIZE", 10 * 1024 * 1024)  # 10MB default
        if file.size > max_size:
            return (
                False,
                f"File size exceeds maximum allowed size of {max_size / (1024 * 1024):.1f}MB",
            )

        # Check file extension
        allowed_extensions = getattr(
            settings, "ALLOWED_IMAGE_EXTENSIONS", ["jpg", "jpeg", "png", "gif", "webp"]
        )
        file_extension = file.name.split(".")[-1].lower() if "." in file.name else ""

        if file_extension not in allowed_extensions:
            return (
                False,
                f"File extension '{file_extension}' not allowed. Allowed extensions: {', '.join(allowed_extensions)}",
            )

        # Check MIME type
        mime_type, _ = mimetypes.guess_type(file.name)
        if not mime_type or not mime_type.startswith("image/"):
            return False, "File must be an image"

        return True, ""

    def generate_unique_filename(self, original_filename: str) -> str:
        """
        Generate a unique filename preserving the extension

        Args:
            original_filename: Original name of the uploaded file

        Returns:
            Unique filename with UUID prefix
        """
        file_extension = (
            original_filename.split(".")[-1].lower()
            if "." in original_filename
            else "jpg"
        )
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        return unique_filename

    def upload_file(self, file, folder: str = "sighting-images") -> Tuple[bool, str]:
        """
        Upload file to Vultr Object Storage

        Args:
            file: Django uploaded file object
            folder: Folder path in the bucket

        Returns:
            Tuple of (success, url_or_error_message)
        """
        try:
            # Validate file
            is_valid, error_message = self.validate_file(file)
            if not is_valid:
                return False, error_message

            # Generate unique filename
            unique_filename = self.generate_unique_filename(file.name)

            # Create full key with folder path
            if folder:
                key = f"{folder.strip('/')}/{unique_filename}"
            else:
                key = unique_filename

            # Determine content type
            content_type, _ = mimetypes.guess_type(file.name)
            if not content_type:
                content_type = "image/jpeg"  # Default fallback

            # Reset file pointer to beginning
            file.seek(0)

            # Upload to Vultr Object Storage
            self.client.upload_fileobj(
                file,
                self.bucket_name,
                key,
                ExtraArgs={
                    "ContentType": content_type,
                    "ACL": "public-read",  # Make the file publicly accessible
                },
            )

            # Generate public URL
            public_url = f"{self.endpoint_url.rstrip('/')}/{self.bucket_name}/{key}"

            return True, public_url

        except NoCredentialsError:
            return False, "Invalid Vultr Object Storage credentials"
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchBucket":
                return False, f"Bucket '{self.bucket_name}' does not exist"
            elif error_code == "AccessDenied":
                return False, "Access denied to Vultr Object Storage"
            else:
                return False, f"Upload failed: {e.response['Error']['Message']}"
        except Exception as e:
            return False, f"Unexpected error during upload: {str(e)}"

    def delete_file(self, file_url: str) -> Tuple[bool, str]:
        """
        Delete file from Vultr Object Storage

        Args:
            file_url: Public URL of the file to delete

        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Extract key from URL
            # Expected format: https://endpoint/bucket/path/filename
            url_parts = file_url.replace(self.endpoint_url.rstrip("/"), "").strip("/")
            if url_parts.startswith(self.bucket_name):
                key = url_parts.replace(self.bucket_name, "", 1).strip("/")
            else:
                return False, "Invalid file URL format"

            if not key:
                return False, "Could not extract file key from URL"

            # Delete from Vultr Object Storage
            self.client.delete_object(Bucket=self.bucket_name, Key=key)

            return True, "File deleted successfully"

        except ClientError as e:
            return False, f"Delete failed: {e.response['Error']['Message']}"
        except Exception as e:
            return False, f"Unexpected error during deletion: {str(e)}"

    def file_exists(self, file_url: str) -> bool:
        """
        Check if file exists in Vultr Object Storage

        Args:
            file_url: Public URL of the file

        Returns:
            True if file exists, False otherwise
        """
        try:
            # Extract key from URL
            url_parts = file_url.replace(self.endpoint_url.rstrip("/"), "").strip("/")
            if url_parts.startswith(self.bucket_name):
                key = url_parts.replace(self.bucket_name, "", 1).strip("/")
            else:
                return False

            if not key:
                return False

            # Check if object exists
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            return True

        except ClientError:
            return False
        except Exception:
            return False


def upload_image_to_vultr(file) -> Tuple[bool, str]:
    """
    Convenience function to upload image to Vultr Object Storage

    Args:
        file: Django uploaded file object

    Returns:
        Tuple of (success, url_or_error_message)
    """
    try:
        manager = VultrObjectStorageManager()
        return manager.upload_file(file)
    except ValueError as e:
        return False, str(e)


def delete_image_from_vultr(file_url: str) -> Tuple[bool, str]:
    """
    Convenience function to delete image from Vultr Object Storage

    Args:
        file_url: Public URL of the file to delete

    Returns:
        Tuple of (success, error_message)
    """
    try:
        manager = VultrObjectStorageManager()
        return manager.delete_file(file_url)
    except ValueError as e:
        return False, str(e)

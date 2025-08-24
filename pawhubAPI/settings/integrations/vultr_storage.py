# Vultr Object Storage Configuration

from pawhubAPI.settings.env import env

# Vultr Object Storage Settings
VULTR_OBJECT_STORAGE_ENABLED = env.bool("VULTR_OBJECT_STORAGE_ENABLED", default=False)

# Vultr Object Storage Credentials
VULTR_ACCESS_KEY_ID = env.str("VULTR_ACCESS_KEY_ID", default="3XBPP2V081DPDI0KM5MC")
VULTR_SECRET_ACCESS_KEY = env.str("VULTR_SECRET_ACCESS_KEY", default="yWmDm5mELAI7kfnYDawDEkxh5wJaJfG3z5mAACrW")
VULTR_ENDPOINT_URL = env.str("VULTR_ENDPOINT_URL", default="https://blr1.vultrobjects.com")
VULTR_REGION = env.str("VULTR_REGION", default="blr1")
VULTR_BUCKET_NAME = env.str("VULTR_BUCKET_NAME", default="pawhub-bucket")

# File Upload Settings
MAX_FILE_SIZE = env.int("MAX_FILE_SIZE", default=10 * 1024 * 1024)  # 10MB default
ALLOWED_IMAGE_EXTENSIONS = ["jpg", "jpeg", "png", "gif", "webp"]

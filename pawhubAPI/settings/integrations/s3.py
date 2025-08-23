# from pawhubAPI.settings import env

# DEFAULT_FILE_STORAGE = "django_s3_storage.storage.S3Storage"


# S3_BUCKET = env.str("STATIC_S3_BUCKET", default="")
# AWS_REGION = env.str("STATIC_S3_REGION", default="")
# AWS_ACCESS_KEY_ID = env.str("STATIC_S3_AWS_ACCESS_KEY_ID", default="")
# AWS_SECRET_ACCESS_KEY = env.str("STATIC_S3_AWS_SECRET_ACCESS_KEY", default="")

# STATICFILES_STORAGE = "django_s3_storage.storage.StaticS3Storage"
# AWS_S3_BUCKET_NAME_STATIC = S3_BUCKET

# # These next two lines will serve the static files directly
# # from the s3 bucket
# AWS_S3_CUSTOM_DOMAIN = "%s.s3.amazonaws.com" % S3_BUCKET
# STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN

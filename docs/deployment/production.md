# Deployment Guide

## Docker Deployment

### Production Build

```bash
# Build Docker image
docker build -t pawhub-api .

# Run with docker-compose
docker-compose up -d
```

### Environment Variables

Set these environment variables for production:

```bash
# Django Configuration
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:pass@db:5432/pawhub_db

# Media Storage (AWS S3)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket

# Security
SECURE_SSL_REDIRECT=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
```

## AWS Deployment

### EC2 Setup

1. **Launch EC2 Instance**

   - Ubuntu 22.04 LTS
   - t3.medium or larger
   - Security groups: 80, 443, 22

2. **Install Dependencies**

   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose nginx certbot
   sudo usermod -aG docker ubuntu
   ```

3. **Deploy Application**
   ```bash
   git clone <repository>
   cd pawhubAPI
   docker-compose -f docker-compose.prod.yml up -d
   ```

### RDS Database

1. **Create RDS Instance**

   - PostgreSQL 14+
   - Enable PostGIS in parameter group
   - Configure security groups

2. **Setup PostGIS**
   ```sql
   CREATE EXTENSION postgis;
   CREATE EXTENSION postgis_topology;
   ```

### S3 Media Storage

Configure S3 bucket for media files:

```python
# settings/production.py
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_S3_REGION_NAME = 'us-west-2'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
```

## Heroku Deployment

### Setup

1. **Install Heroku CLI**
2. **Create Heroku App**

   ```bash
   heroku create pawhub-api
   heroku addons:create heroku-postgresql:hobby-dev
   ```

3. **Configure Environment**

   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=pawhub-api.herokuapp.com
   ```

4. **Deploy**
   ```bash
   git push heroku main
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

### PostGIS on Heroku

Enable PostGIS extension:

```bash
heroku pg:psql
CREATE EXTENSION postgis;
```

## Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/static/files/;
    }

    location /media/ {
        alias /path/to/media/files/;
    }
}
```

## SSL Configuration

```bash
# Install SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
0 12 * * * /usr/bin/certbot renew --quiet
```

## Monitoring

### Health Checks

Add health check endpoint:

```python
# views.py
class HealthCheckAPI(APIView):
    permission_classes = []
    authentication_classes = []

    def get(self, request):
        return Response({"status": "healthy"})
```

### Logging

Configure production logging:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/error.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

## Backup Strategy

### Database Backups

```bash
# Daily backup script
#!/bin/bash
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
aws s3 cp backup_$(date +%Y%m%d).sql s3://your-backup-bucket/
```

### Media Backups

S3 versioning and cross-region replication recommended.

## Performance Tuning

### Gunicorn Configuration

```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
keepalive = 2
```

### PostgreSQL Tuning

```sql
-- postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
```

## Security Checklist

- [ ] Use HTTPS only
- [ ] Set secure headers
- [ ] Regular security updates
- [ ] Database connection encryption
- [ ] Secure secret management
- [ ] API rate limiting
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection

## Troubleshooting

### Common Issues

1. **Database Connection**

   ```bash
   # Test database connection
   python manage.py dbshell
   ```

2. **Static Files**

   ```bash
   # Collect static files
   python manage.py collectstatic --noinput
   ```

3. **Migrations**

   ```bash
   # Check migration status
   python manage.py showmigrations
   ```

4. **Logs**
   ```bash
   # View application logs
   docker logs pawhub-api
   tail -f /var/log/django/error.log
   ```

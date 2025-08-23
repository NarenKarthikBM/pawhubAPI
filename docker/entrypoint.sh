#!/usr/bin/env bash
set -e

# Wait for DB
echo "Waiting for database..."
python - <<'PYCODE'
import os, time, sys
import psycopg
from urllib.parse import urlparse
url = urlparse(os.getenv("DATABASE_URL"))
for i in range(60):
    try:
        psycopg.connect(
            host=url.hostname, port=url.port or 5432,
            user=url.username, password=url.password, dbname=url.path.lstrip("/")
        ).close()
        sys.exit(0)
    except Exception:
        time.sleep(1)
print("DB not ready after 60s", file=sys.stderr)
sys.exit(1)
PYCODE

# Run app
exec gunicorn myproject.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 60
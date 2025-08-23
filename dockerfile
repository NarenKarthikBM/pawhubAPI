FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps for GeoDjango
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    binutils \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    proj-bin \
    && rm -rf /var/lib/apt/lists/*

# Ensure GDAL is discoverable (optional on manylinux wheels, safe to keep)
ENV GDAL_DATA=/usr/share/gdal
ENV PROJ_LIB=/usr/share/proj

WORKDIR /app

# Install deps via pipenv into system site-packages
COPY Pipfile Pipfile.lock ./
RUN pip install --upgrade pip pipenv && \
    pipenv install --deploy --system

# Project files
COPY . .

# Entrypoint (waits for DB, etc.)
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
CMD ["/entrypoint.sh"]
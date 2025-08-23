FROM python:3.11-slim

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

# Ensure GDAL is discoverable
ENV GDAL_DATA=/usr/share/gdal
ENV PROJ_LIB=/usr/share/proj

WORKDIR /app

# Install pipenv first
RUN pip install --upgrade pip pipenv

# Copy Pipfile and lock file
COPY Pipfile Pipfile.lock ./

# Install most deps via pipenv (excluding GDAL)
RUN pipenv install --deploy --system

# Install GDAL separately with version matching system GDAL
RUN GDAL_VERSION=$(gdal-config --version) && \
    echo "Installing GDAL Python bindings for GDAL $GDAL_VERSION" && \
    pip install GDAL==$GDAL_VERSION

# Project files
COPY . .

# Entrypoint (waits for DB, etc.)
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000
CMD ["/entrypoint.sh"]
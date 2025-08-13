#!/bin/bash
# Build script for deployment platforms like Render

# Upgrade pip
pip install --upgrade pip

# Try to install with pre-built wheels first
if pip install --only-binary=all -r requirements.txt; then
    echo "Successfully installed with pre-built wheels"
else
    echo "Pre-built wheels failed, trying fallback installation..."
    pip install -r requirements-fallback.txt
fi

# Run migrations
python manage.py migrate --noinput

# Collect static files
python manage.py collectstatic --noinput --clear
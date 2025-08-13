#!/bin/bash
# For deployment environments like Render

# Upgrade pip first
pip install --upgrade pip

# Install packages with pre-built wheels only (no source compilation)
pip install --only-binary=all -r requirements-fixed.txt

# If that fails, install without build isolation
pip install --no-build-isolation -r requirements-fixed.txt
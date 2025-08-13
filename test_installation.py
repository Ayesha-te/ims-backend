#!/usr/bin/env python
"""
Test script to verify the Django installation works correctly
"""
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def test_installation():
    """Test if the Django application can start properly"""
    print("Testing Halal Inventory System installation...")
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'halal_inventory_system.settings')
    django.setup()
    
    # Check if all apps are properly installed
    from django.apps import apps
    print("✓ Django apps loaded successfully")
    
    # Check database connection
    from django.db import connection
    try:
        connection.ensure_connection()
        print("✓ Database connection working")
    except Exception as e:
        print(f"⚠ Database connection issue: {e}")
    
    # Check if models can be imported
    try:
        from inventory.models import Product, Category, Supplier, StockAlert
        print("✓ Inventory models imported successfully")
    except Exception as e:
        print(f"⚠ Model import issue: {e}")
    
    # Check if views can be imported
    try:
        from inventory.views import ProductViewSet, CategoryViewSet
        print("✓ Views imported successfully")
    except Exception as e:
        print(f"⚠ Views import issue: {e}")
    
    print("\nInstallation test completed!")

if __name__ == '__main__':
    test_installation()
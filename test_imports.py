#!/usr/bin/env python
"""
Test script to verify all imports work correctly
"""
import os
import sys
import traceback

def test_django_setup():
    """Test Django setup and app loading"""
    try:
        print("Testing Django setup...")
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'halal_inventory_system.settings')
        
        import django
        print(f"Django version: {django.get_version()}")
        
        django.setup()
        print("✓ Django setup successful")
        
        # Test importing models
        from inventory.models import Product, Category, Supplier
        print("✓ Models imported successfully")
        
        # Test importing views
        from inventory.views import CategoryViewSet
        print("✓ Views imported successfully")
        
        # Test WSGI application
        from halal_inventory_system.wsgi import application
        print("✓ WSGI application loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Error during Django setup: {str(e)}")
        print(f"Exception type: {type(e).__name__}")
        print("Full traceback:")
        traceback.print_exc()
        return False

def test_required_packages():
    """Test that all required packages can be imported"""
    required_packages = [
        'django',
        'rest_framework',
        'corsheaders',
        'rest_framework_simplejwt',
        'PIL',
        'barcode',
        'qrcode',
        'requests',
        'decouple',
        'django_crontab',
        'reportlab',
        'gunicorn',
        'psycopg2',
        'dj_database_url',
        'whitenoise',
        'openpyxl'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError as e:
            print(f"✗ {package}: {str(e)}")
            failed_imports.append(package)
    
    return len(failed_imports) == 0, failed_imports

if __name__ == "__main__":
    print("=" * 50)
    print("TESTING PACKAGE IMPORTS")
    print("=" * 50)
    
    packages_ok, failed = test_required_packages()
    
    print("\n" + "=" * 50)
    print("TESTING DJANGO SETUP")
    print("=" * 50)
    
    django_ok = test_django_setup()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    if packages_ok and django_ok:
        print("✓ All tests passed! Application should deploy successfully.")
        sys.exit(0)
    else:
        print("✗ Some tests failed:")
        if not packages_ok:
            print(f"  - Failed package imports: {', '.join(failed)}")
        if not django_ok:
            print("  - Django setup failed")
        sys.exit(1)
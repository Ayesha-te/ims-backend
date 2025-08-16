#!/usr/bin/env python
"""
Deployment readiness check script
Run this before deploying to ensure everything is ready
"""
import os
import sys

def main():
    print("🚀 Deployment Readiness Check")
    print("=" * 40)
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'halal_inventory_system.settings')
    
    try:
        # Test Django setup
        import django
        django.setup()
        
        # Test critical imports
        from inventory.models import Product
        from inventory.views import CategoryViewSet
        from halal_inventory_system.wsgi import application
        
        # Test database configuration
        from django.conf import settings
        print(f"✓ Django version: {django.get_version()}")
        print(f"✓ Debug mode: {settings.DEBUG}")
        print(f"✓ Database engine: {settings.DATABASES['default']['ENGINE']}")
        print(f"✓ Allowed hosts: {settings.ALLOWED_HOSTS}")
        
        # Test WSGI
        print("✓ WSGI application loads successfully")
        
        # Run Django checks
        from django.core.management import execute_from_command_line
        print("✓ Running Django system checks...")
        execute_from_command_line(['manage.py', 'check'])
        
        print("\n🎉 All checks passed! Ready for deployment.")
        return True
        
    except Exception as e:
        print(f"❌ Deployment check failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
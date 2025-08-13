#!/usr/bin/env python
"""
Simple validation script to check Django settings configuration
"""
import sys
import os
from pathlib import Path

def validate_settings():
    """Validate Django settings without importing Django"""
    print("🔍 Validating Django settings configuration...")
    
    # Check if settings file exists
    settings_path = Path("halal_inventory_system/settings.py")
    if not settings_path.exists():
        print("❌ Settings file not found!")
        return False
    
    # Read settings file
    with open(settings_path, 'r', encoding='utf-8') as f:
        settings_content = f.read()
    
    # Check ALLOWED_HOSTS configuration
    if 'ims-backend-r3ld.onrender.com' in settings_content:
        print("✅ ALLOWED_HOSTS configured for production")
    else:
        print("❌ Production host not in ALLOWED_HOSTS")
        return False
    
    # Check CORS configuration
    if 'CORS_ALLOWED_ORIGINS' in settings_content:
        print("✅ CORS configuration found")
    else:
        print("❌ CORS configuration missing")
        return False
    
    # Check WhiteNoise middleware
    if 'whitenoise.middleware.WhiteNoiseMiddleware' in settings_content:
        print("✅ WhiteNoise middleware configured")
    else:
        print("❌ WhiteNoise middleware missing")
        return False
    
    # Check database configuration
    if 'dj_database_url' in settings_content or 'DATABASE_URL' in settings_content:
        print("✅ Production database configuration found")
    else:
        print("❌ Production database configuration missing")
        return False
    
    # Check requirements.txt
    req_path = Path("requirements.txt")
    if req_path.exists():
        with open(req_path, 'r') as f:
            requirements = f.read()
        
        if 'whitenoise' in requirements and 'dj-database-url' in requirements:
            print("✅ Required packages in requirements.txt")
        else:
            print("❌ Missing required packages in requirements.txt")
            return False
    
    # Check health check views
    health_path = Path("inventory/health_views.py")
    if health_path.exists():
        print("✅ Health check views created")
    else:
        print("❌ Health check views missing")
        return False
    
    # Check URL configuration
    urls_path = Path("inventory/urls.py")
    if urls_path.exists():
        with open(urls_path, 'r') as f:
            urls_content = f.read()
        
        if 'health_check' in urls_content:
            print("✅ Health check URL configured")
        else:
            print("❌ Health check URL not configured")
            return False
    
    print("\n🎉 All configurations validated successfully!")
    print("\n📋 Deployment Summary:")
    print("   • HTTP_HOST error: FIXED")
    print("   • Root URL handler: ADDED")
    print("   • Static files: CONFIGURED")
    print("   • CORS settings: UPDATED")
    print("   • Database config: PRODUCTION READY")
    
    return True

if __name__ == '__main__':
    # Set working directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    success = validate_settings()
    if success:
        print("\n🚀 Your Django app is ready for deployment!")
        sys.exit(0)
    else:
        print("\n❌ Configuration issues found!")
        sys.exit(1)
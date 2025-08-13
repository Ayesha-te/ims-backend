#!/usr/bin/env python
"""
Startup script for the Halal Inventory Management System
This script handles all the necessary setup and starts the Django development server
"""

import os
import sys
import subprocess
import django
from pathlib import Path

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'halal_inventory_system.settings')
    django.setup()

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} failed")
            if result.stderr:
                print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False
    return True

def main():
    print("🚀 Starting Halal Inventory Management System...")
    print("=" * 60)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  WARNING: No virtual environment detected.")
        print("   It's recommended to use a virtual environment.")
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    # Install/upgrade dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies. Please run: pip install -r requirements.txt")
        return
    
    # Setup Django
    try:
        setup_django()
        print("✅ Django setup completed")
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return
    
    # Create database and run migrations
    if not run_command("python manage.py makemigrations", "Creating migrations"):
        return
    
    if not run_command("python manage.py migrate", "Running migrations"):
        return
    
    # Create superuser if needed
    print("🔧 Setting up initial data...")
    run_command("python manage.py setup_inventory --admin-user admin --with-sample-data", "Setting up inventory data")
    
    # Generate initial alerts
    run_command("python manage.py generate_alerts", "Generating expiry alerts")
    
    # Collect static files (for production)
    run_command("python manage.py collectstatic --noinput", "Collecting static files")
    
    print("\n" + "=" * 60)
    print("🎉 Halal Inventory Management System is ready!")
    print("📋 System Information:")
    print("   • Admin Panel: http://localhost:8000/admin/")
    print("   • API Root: http://localhost:8000/api/")
    print("   • Admin Username: admin")
    print("   • Admin Password: admin123")
    print("\n💡 API Endpoints:")
    print("   • Products: http://localhost:8000/api/products/")
    print("   • Barcode Scan: http://localhost:8000/api/products/scan_barcode/")
    print("   • Expiry Alerts: http://localhost:8000/api/expiry-alerts/")
    print("   • Dashboard: http://localhost:8000/api/dashboard/stats/")
    print("\n🔧 Additional Commands:")
    print("   • Generate Alerts: python manage.py generate_alerts")
    print("   • Setup Data: python manage.py setup_inventory --help")
    print("   • Start Celery: celery -A halal_inventory_system worker -l info")
    print("\n🌟 Starting Django development server...")
    print("=" * 60)
    
    # Start the development server
    try:
        subprocess.run("python manage.py runserver", shell=True, cwd=Path(__file__).parent)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")

if __name__ == "__main__":
    main()
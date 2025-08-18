#!/usr/bin/env python3
"""
Test script for registration endpoint
Run this to test the backend registration directly
"""

import requests
import json
import sys
import os

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_registration_endpoint():
    """Test the registration endpoint directly"""
    
    # Test data
    test_data = {
        "name": "Test Supermarket",
        "email": "test@example.com", 
        "password": "testpassword123",
        "confirm_password": "testpassword123",
        "address": "123 Test Street, Test City",
        "phone": "+1234567890",
        "description": "A test supermarket for debugging"
    }
    
    # API endpoint
    base_url = "https://ims-backend-r3ld.onrender.com"
    endpoint = f"{base_url}/api/auth/register/"
    
    print("🚀 Testing registration endpoint...")
    print(f"URL: {endpoint}")
    print(f"Data: {json.dumps({**test_data, 'password': '[HIDDEN]', 'confirm_password': '[HIDDEN]'}, indent=2)}")
    
    try:
        response = requests.post(
            endpoint,
            json=test_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📊 Response Data: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"📊 Response Text: {response.text}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            return True
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

def test_local_registration():
    """Test registration on local Django server"""
    
    test_data = {
        "name": "Local Test Supermarket",
        "email": "local@example.com",
        "password": "localpassword123", 
        "confirm_password": "localpassword123",
        "address": "123 Local Street",
        "phone": "+1234567890",
        "description": "Local test supermarket"
    }
    
    endpoint = "http://localhost:8000/api/auth/register/"
    
    print("\n🏠 Testing local registration endpoint...")
    print(f"URL: {endpoint}")
    
    try:
        response = requests.post(
            endpoint,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📊 Local Response Status: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"📊 Local Response Data: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"📊 Local Response Text: {response.text}")
            
        return response.status_code == 201
        
    except requests.exceptions.ConnectionError:
        print("❌ Local server not running")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Local request error: {e}")
        return False

def test_serializer_validation():
    """Test different validation scenarios"""
    
    scenarios = [
        {
            "name": "Valid Data",
            "data": {
                "name": "Valid Market",
                "email": "valid@test.com",
                "password": "validpass123",
                "confirm_password": "validpass123", 
                "address": "123 Valid St",
                "phone": "+1234567890",
                "description": "Valid test"
            }
        },
        {
            "name": "Password Mismatch",
            "data": {
                "name": "Mismatch Market",
                "email": "mismatch@test.com",
                "password": "password123",
                "confirm_password": "different123",
                "address": "123 Test St",
                "phone": "+1234567890"
            }
        },
        {
            "name": "Missing Required Fields",
            "data": {
                "email": "missing@test.com",
                "password": "password123",
                "confirm_password": "password123"
            }
        },
        {
            "name": "Invalid Email",
            "data": {
                "name": "Invalid Email Market",
                "email": "invalid-email",
                "password": "password123",
                "confirm_password": "password123",
                "address": "123 Test St",
                "phone": "+1234567890"
            }
        }
    ]
    
    base_url = "https://ims-backend-r3ld.onrender.com"
    endpoint = f"{base_url}/api/auth/register/"
    
    print("\n🧪 Testing validation scenarios...")
    
    for scenario in scenarios:
        print(f"\n--- Testing: {scenario['name']} ---")
        
        try:
            response = requests.post(
                endpoint,
                json=scenario['data'],
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            print(f"Status: {response.status_code}")
            
            try:
                data = response.json()
                if response.status_code >= 400:
                    print(f"Expected error: {json.dumps(data, indent=2)}")
                else:
                    print(f"Unexpected success: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Response text: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")

if __name__ == "__main__":
    print("🔧 Django Registration Endpoint Test")
    print("=" * 50)
    
    # Test remote endpoint
    success = test_registration_endpoint()
    
    # Test local endpoint if available
    test_local_registration()
    
    # Test validation scenarios
    test_serializer_validation()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
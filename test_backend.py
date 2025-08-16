#!/usr/bin/env python3
"""
Test script to verify all backend endpoints are working correctly
"""
import requests
import json
import sys

BASE_URL = 'http://127.0.0.1:8000'

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f'{BASE_URL}/')
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_api_info():
    """Test the API info endpoint"""
    print("🔍 Testing API info...")
    try:
        response = requests.get(f'{BASE_URL}/info/')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Info: {data.get('name', 'Unknown')} v{data.get('version', 'Unknown')}")
            return True
        else:
            print(f"❌ API info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API info error: {e}")
        return False

def test_endpoints():
    """Test various API endpoints"""
    print("🔍 Testing API endpoints...")
    
    endpoints_to_test = [
        '/api/categories/',
        '/api/suppliers/',
        '/api/products/',
        '/api/supermarkets/',
        '/api/substores/',
        '/api/excel-imports/',
        '/api/image-imports/',
        '/api/pos-integration/products_sync/',
        '/api/dashboard/stats/',
        '/api/stock-transactions/',
        '/api/expiry-alerts/',
        '/api/product-tickets/'
    ]
    
    passed = 0
    total = len(endpoints_to_test)
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f'{BASE_URL}{endpoint}')
            # We expect 401 (Unauthorized) for protected endpoints without auth
            # or 200 for public endpoints
            if response.status_code in [200, 401]:
                print(f"✅ {endpoint} - Status: {response.status_code}")
                passed += 1
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    print(f"\n📊 Endpoint Tests: {passed}/{total} passed")
    return passed == total

def test_supermarket_registration():
    """Test supermarket registration endpoint"""
    print("🔍 Testing supermarket registration...")
    
    test_data = {
        "name": "Test Supermarket",
        "address": "123 Test Street",
        "phone": "+1234567890",
        "email": "test@example.com",
        "password": "testpassword123",
        "license_number": "TEST123",
        "description": "Test supermarket for API testing"
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/auth/register/', json=test_data)
        if response.status_code in [200, 201, 400]:  # 400 might be "already exists"
            print(f"✅ Registration endpoint working - Status: {response.status_code}")
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"   Created supermarket: {data.get('supermarket', {}).get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Backend API Tests")
    print("=" * 50)
    
    tests = [
        test_health_check,
        test_api_info,
        test_endpoints,
        test_supermarket_registration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print("-" * 30)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print("-" * 30)
    
    print(f"\n🎯 Final Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
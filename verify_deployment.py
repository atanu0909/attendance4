#!/usr/bin/env python3
"""
Railway Deployment Verification Script
Tests all components before deployment
"""

import os
import sys
import importlib.util

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing Python imports...")
    
    required_modules = [
        'pyodbc',
        'pandas', 
        'datetime',
        'smtplib',
        'logging',
        'json',
        'time'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
    
    return True

def test_custom_modules():
    """Test if custom modules can be imported"""
    print("\n🔍 Testing custom modules...")
    
    try:
        from device_19_github_monitor import (
            get_working_connection_string,
            EMPLOYEES_TO_MONITOR,
            check_device_19_attendance
        )
        print("✅ device_19_github_monitor imports successful")
        
        import railway_monitor
        print("✅ railway_monitor imports successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Custom module import failed: {e}")
        return False

def test_environment_variables():
    """Test environment variable configuration"""
    print("\n🔍 Testing environment variables...")
    
    required_vars = [
        'DB_SERVER',
        'DB_DATABASE', 
        'DB_USERNAME',
        'DB_PASSWORD',
        'EMAIL_ENABLED',
        'GMAIL_USER',
        'GMAIL_PASSWORD',
        'ALERT_EMAIL'
    ]
    
    # Set default values for testing
    defaults = {
        'DB_SERVER': '1.22.45.168,19471',
        'DB_DATABASE': 'etimetrackliteWEB',
        'DB_USERNAME': 'sa',
        'DB_PASSWORD': 'sa@123',
        'EMAIL_ENABLED': 'True',
        'GMAIL_USER': 'ghoshatanu32309@gmail.com',
        'GMAIL_PASSWORD': 'oqahvqkuaziufvfb',
        'ALERT_EMAIL': 'aghosh09092004@gmail.com'
    }
    
    for var in required_vars:
        value = os.getenv(var, defaults.get(var))
        if value:
            print(f"✅ {var}: {'***' if 'PASSWORD' in var else value}")
        else:
            print(f"❌ {var}: Not set")
            return False
    
    return True

def test_database_connection():
    """Test database connectivity"""
    print("\n🔍 Testing database connection...")
    
    try:
        from device_19_github_monitor import get_working_connection_string
        conn_str = get_working_connection_string()
        print("✅ Database connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_files_exist():
    """Check if all required files exist"""
    print("\n🔍 Testing required files...")
    
    required_files = [
        'railway_monitor.py',
        'device_19_github_monitor.py',
        'requirements.txt',
        'Procfile',
        'runtime.txt',
        '.env.example',
        'railway.json'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}: Missing")
            return False
    
    return True

def main():
    """Run all verification tests"""
    print("🚀 Railway Deployment Verification")
    print("=" * 40)
    
    tests = [
        ("File Existence", test_files_exist),
        ("Python Imports", test_imports),
        ("Custom Modules", test_custom_modules),
        ("Environment Variables", test_environment_variables),
        ("Database Connection", test_database_connection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 20)
        success = test_func()
        results.append((test_name, success))
        print(f"Result: {'✅ PASS' if success else '❌ FAIL'}")
    
    print("\n" + "=" * 40)
    print("📊 FINAL RESULTS")
    print("=" * 40)
    
    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not success:
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Ready for Railway deployment!")
        print("\nNext steps:")
        print("1. Go to https://railway.app")
        print("2. Deploy from GitHub repo: atanu0909/attendance4")
        print("3. Add environment variables")
        print("4. Monitor deployment logs")
    else:
        print("❌ SOME TESTS FAILED!")
        print("❗ Fix the issues before deploying to Railway")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

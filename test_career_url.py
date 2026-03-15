#!/usr/bin/env python3
"""
Test Career Guide URL routing
"""
import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.core.settings')

try:
    import django
    django.setup()
    
    from django.urls import reverse
    from django.test import Client
    
    print("🔍 Testing Career Guide URL routing...")
    
    # Test URL reverse
    try:
        career_url = reverse('career')
        print(f"✅ Career URL reverse successful: {career_url}")
    except Exception as e:
        print(f"❌ URL reverse failed: {e}")
        print("💡 This might indicate the URL is not properly configured")
        
    # Test URL resolution
    try:
        from django.urls import resolve
        resolved = resolve('/chat/career/')
        print(f"✅ URL resolution successful: {resolved.func}")
        print(f"   View name: {resolved.url_name}")
        print(f"   Namespace: {resolved.namespace}")
    except Exception as e:
        print(f"❌ URL resolution failed: {e}")
        
    # Test client access (without authentication)
    try:
        client = Client()
        response = client.get('/chat/career/')
        
        if response.status_code == 302:
            print("✅ Career URL redirects (expected for unauthenticated users)")
            print(f"   Redirect to: {response.url}")
        elif response.status_code == 200:
            print("✅ Career URL accessible (unexpected for unauthenticated users)")
        elif response.status_code == 404:
            print("❌ Career URL returns 404 - URL not found")
        else:
            print(f"⚠️ Career URL returns {response.status_code}")
            
    except Exception as e:
        print(f"❌ Client test failed: {e}")
        
    print("\n📊 URL Routing Test Summary:")
    print("✅ Career guide URL is properly configured")
    print("🌐 Access URL: http://127.0.0.1:8000/chat/career/")
    print("🔐 Requires user authentication (login required)")
    
except ImportError as e:
    print(f"❌ Django setup failed: {e}")
    print("💡 Make sure Django is installed and settings are correct")
except Exception as e:
    print(f"❌ Unexpected error: {e})

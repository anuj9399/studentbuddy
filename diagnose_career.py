#!/usr/bin/env python3
"""
Simple diagnostic script for Career Guide feature
"""
import os
import sys

def check_file_structure():
    """Check if all required files exist"""
    print("🔍 Checking file structure...")
    
    required_files = [
        'core/ai/views.py',
        'core/ai/urls.py',
        'core/templates/ai/career.html',
        'core/core/urls.py',
        'core/core/settings.py',
        'urls.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files exist")
        return True

def check_url_configuration():
    """Check URL configuration"""
    print("\n🔍 Checking URL configuration...")
    
    try:
        # Check if AI app is included in core URLs
        with open('core/core/urls.py', 'r') as f:
            core_urls_content = f.read()
            
        if "path('chat/', include('ai.urls'))" in core_urls_content:
            print("✅ AI app included in core URLs")
        else:
            print("❌ AI app not included in core URLs")
            return False
            
        # Check if career URL is defined in AI URLs
        with open('core/ai/urls.py', 'r') as f:
            ai_urls_content = f.read()
            
        if "path('career/', views.career, name='career')" in ai_urls_content:
            print("✅ Career URL defined in AI URLs")
        else:
            print("❌ Career URL not defined in AI URLs")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking URLs: {e}")
        return False

def check_view_function():
    """Check if career view function exists"""
    print("\n🔍 Checking career view function...")
    
    try:
        with open('core/ai/views.py', 'r') as f:
            views_content = f.read()
            
        if "def career(request):" in views_content:
            print("✅ Career view function exists")
            
            # Check if it has the login_required decorator
            if "@login_required" in views_content and "def career(request):" in views_content:
                print("✅ Career view has login_required decorator")
            else:
                print("⚠️ Career view might be missing login_required decorator")
                
            return True
        else:
            print("❌ Career view function not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking view: {e}")
        return False

def check_template():
    """Check if career template exists and has required elements"""
    print("\n🔍 Checking career template...")
    
    try:
        with open('core/templates/ai/career.html', 'r') as f:
            template_content = f.read()
            
        required_elements = [
            'extends "base.html"',
            'method="POST"',
            'name="stream"',
            '{% if careers %}',
            '{% for career in careers %}',
            'career.title',
            'career.match_percentage'
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in template_content:
                missing_elements.append(element)
            else:
                print(f"✅ Template element: {element}")
        
        if missing_elements:
            print(f"❌ Missing template elements: {missing_elements}")
            return False
        else:
            print("✅ All required template elements present")
            return True
            
    except Exception as e:
        print(f"❌ Error checking template: {e}")
        return False

def check_settings():
    """Check Django settings"""
    print("\n🔍 Checking Django settings...")
    
    try:
        with open('core/core/settings.py', 'r') as f:
            settings_content = f.read()
            
        # Check if AI app is in INSTALLED_APPS
        if "'ai'," in settings_content or '"ai",' in settings_content:
            print("✅ AI app in INSTALLED_APPS")
        else:
            print("❌ AI app not in INSTALLED_APPS")
            return False
            
        # Check if OPENROUTER_API_KEY is configured
        if "OPENROUTER_API_KEY" in settings_content:
            print("✅ OPENROUTER_API_KEY configured")
        else:
            print("❌ OPENROUTER_API_KEY not configured")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking settings: {e}")
        return False

def main():
    print("🚀 Career Guide Feature Diagnostic")
    print("=" * 50)
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run all checks
    checks = [
        check_file_structure,
        check_url_configuration,
        check_view_function,
        check_template,
        check_settings
    ]
    
    results = []
    for check in checks:
        results.append(check())
    
    # Summary
    print("\n📊 Diagnostic Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All checks passed! Career Guide feature should be working.")
        print("\n🌐 Access it at: http://127.0.0.1:8000/chat/career/")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        
        print("\n🔧 Common fixes:")
        print("1. Ensure all required files exist")
        print("2. Check URL configurations")
        print("3. Verify OPENROUTER_API_KEY is set")
        print("4. Run migrations: python manage.py migrate")
        print("5. Start server: python manage.py runserver")

if __name__ == "__main__":
    main()

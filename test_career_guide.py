#!/usr/bin/env python3
"""
Test script to check Career Guide functionality
"""
import os
import sys
import django
import requests
import json

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.core.settings')
django.setup()

def test_career_api():
    """Test the OpenRouter API for career predictions"""
    print("🔍 Testing Career Guide API...")
    
    # Check API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in environment variables")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test API call
    try:
        prompt = """You are a comprehensive career counselor for Indian students.
For the academic stream "Computer Science", provide exactly 2 career paths.

Return ONLY valid JSON in this exact format, no markdown, no extra text:
{
  "careers": [
    {
      "title": "Career Title",
      "field": "Field/Domain",
      "description": "2-3 sentence description of this career",
      "match_percentage": 95,
      "avg_salary": "₹X LPA - ₹Y LPA",
      "growth": "High/Medium/Low",
      "education": "Required degree",
      "skills": ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"],
      "job_outlook": "2-3 sentences about job market",
      "industries": ["Industry 1", "Industry 2", "Industry 3", "Industry 4"],
      "career_steps": [
        {"step": 1, "title": "Step title", "description": "What to do", "duration": "X years"},
        {"step": 2, "title": "Step title", "description": "What to do", "duration": "X years"}
      ]
    }
  ]
}"""

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "anthropic/claude-3-haiku",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ API call successful")
            response_data = response.json()
            raw_content = response_data['choices'][0]['message']['content']
            
            # Strip markdown and parse JSON
            raw_content = raw_content.replace('```json', '').replace('```', '').strip()
            data = json.loads(raw_content)
            careers = data.get('careers', [])
            
            print(f"✅ Successfully parsed {len(careers)} career paths")
            for career in careers:
                print(f"  - {career.get('title', 'N/A')} ({career.get('match_percentage', 0)}% match)")
            
            return True
            
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        return False
    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_career_view():
    """Test the Django career view"""
    print("\n🔍 Testing Career View...")
    
    try:
        from ai.views import career
        print("✅ Career view imported successfully")
        
        # Test view function exists
        if callable(career):
            print("✅ Career view is callable")
            return True
        else:
            print("❌ Career view is not callable")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_career_template():
    """Test if career template exists"""
    print("\n🔍 Testing Career Template...")
    
    template_path = os.path.join(os.path.dirname(__file__), 'core', 'templates', 'ai', 'career.html')
    if os.path.exists(template_path):
        print("✅ Career template exists")
        return True
    else:
        print(f"❌ Career template not found at {template_path}")
        return False

def main():
    print("🚀 Career Guide Feature Test")
    print("=" * 50)
    
    results = []
    
    # Test API
    results.append(test_career_api())
    
    # Test view
    results.append(test_career_view())
    
    # Test template
    results.append(test_career_template())
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    if all(results):
        print("✅ All tests passed! Career Guide feature should be working.")
    else:
        print("❌ Some tests failed. Career Guide feature may have issues.")
        
        # Provide troubleshooting tips
        print("\n🔧 Troubleshooting Tips:")
        print("1. Ensure OPENROUTER_API_KEY is set in environment variables")
        print("2. Check internet connection for API calls")
        print("3. Verify the career template exists")
        print("4. Check Django URLs configuration")

if __name__ == "__main__":
    main()

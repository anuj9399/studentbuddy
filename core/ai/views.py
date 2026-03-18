from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
import requests
from django.conf import settings

def call_groq(prompt, max_tokens=1000, system_prompt=None):
    try:
        api_key = settings.GROQ_API_KEY
        
        if not api_key:
            return None, "Groq API key not configured"
        
        messages = []
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        messages.append({
            'role': 'user',
            'content': prompt
        })
        
        response = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': 'llama-3.1-8b-instant',
                'messages': messages,
                'max_tokens': max_tokens,
                'temperature': 0.7,
            },
            timeout=30
        )
        
        print(f"Groq Status: {response.status_code}")
        
        if response.status_code != 200:
            return None, f"API Error {response.status_code}: {response.text[:200]}"
        
        data = response.json()
        content = data['choices'][0]['message']['content'].strip()
        return content, None
        
    except requests.exceptions.Timeout:
        return None, "Request timed out. Please try again."
    except Exception as e:
        print(f"Groq Error: {str(e)}")
        return None, str(e)

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import requests
from pypdf import PdfReader
import os
import tempfile
from accounts.models import StudyActivity, MasteryProgress
from .models import StudyPlan, PlanSubject, StudySession, StudyProgress


# -------------------------
# AI CHAT (Study Assistant)
# -------------------------

@login_required
def chat(request):
    response_text = ""

    if request.method == "POST":
        user_message = request.POST.get("message", "")

        if user_message:
            content, error = call_groq(
                user_message,
                max_tokens=800,
                system_prompt="You are StudentBuddy AI, a helpful academic assistant for Indian engineering students. Give clear, concise answers."
            )
            
            if error:
                response_text = f"Error: {error}"
            else:
                response_text = content

    return render(request, "ai/chat.html", {
        "response": response_text
    })


# -------------------------
# SMART NOTES SUMMARIZER
# -------------------------

@login_required
def smart_notes(request):
    summary = None

    if request.method == "POST":
        print("=== SMART NOTES DEBUG START ===")
        print("POST data:", request.POST)
        print("FILES data:", request.FILES)
        
        notes = request.POST.get("notes", "")
        pdf_file = request.FILES.get("pdf")

        final_text = ""
        pdf_processed = False

        if pdf_file:
            print(f"PDF file detected: {pdf_file.name}")
            print(f"PDF file size: {pdf_file.size} bytes")
            print(f"PDF file content type: {pdf_file.content_type}")
            
            try:
                # Reset file pointer to beginning
                pdf_file.seek(0)
                
                reader = PdfReader(pdf_file)
                print(f"PDF has {len(reader.pages)} pages")
                
                pdf_text = ""
                for i, page in enumerate(reader.pages):
                    try:
                        text = page.extract_text()
                        print(f"Page {i+1}: Extracted {len(text) if text else 0} characters")
                        if text and text.strip():
                            pdf_text += text + "\n"
                    except Exception as page_error:
                        print(f"Error processing page {i+1}: {str(page_error)}")
                        continue
                
                print(f"Total PDF text extracted: {len(pdf_text)} characters")
                print(f"PDF text preview (first 200 chars): {repr(pdf_text[:200])}")
                
                if pdf_text.strip():
                    final_text = pdf_text
                    pdf_processed = True
                    print("✅ PDF processed successfully")
                else:
                    print("❌ PDF contains no extractable text, trying OCR...")
                    
                    # Try OCR as fallback
                    try:
                        try:
                            from pdf2image import convert_from_bytes
                            PDF2IMAGE_AVAILABLE = True
                        except ImportError:
                            print("❌ pdf2image not available - skipping OCR")
                            pdf_processed = True
                            final_text = ""
                        else:
                            import pytesseract
                            
                            # Reset file pointer to beginning
                            pdf_file.seek(0)
                            
                            # Set Poppler path for Windows
                            import os
                            if os.name == 'nt':  # Windows
                                poppler_path = r"C:\poppler\poppler-23.07.0\Library\bin"
                                if os.path.exists(poppler_path):
                                    os.environ['PATH'] = poppler_path + ';' + os.environ.get('PATH', '')
                                    print(f"✅ Poppler path set: {poppler_path}")
                                else:
                                    print(f"⚠️ Poppler not found at {poppler_path}")
                                
                                # Set Tesseract path for Windows
                                tesseract_path = r"C:\Program Files\Tesseract-OCR"
                                if os.path.exists(tesseract_path):
                                    os.environ['PATH'] = tesseract_path + ';' + os.environ.get('PATH', '')
                                    print(f"✅ Tesseract path set: {tesseract_path}")
                                else:
                                    print(f"⚠️ Tesseract not found at {tesseract_path}")
                            
                            # Convert PDF to images
                            images = convert_from_bytes(pdf_file.read())
                            print(f"Converted PDF to {len(images)} images for OCR")
                            
                            ocr_text = ""
                            for i, image in enumerate(images):
                                try:
                                    text = pytesseract.image_to_string(image)
                                    print(f"OCR Page {i+1}: Extracted {len(text)} characters")
                                    if text and text.strip():
                                        ocr_text += text + "\n"
                                except Exception as ocr_error:
                                    print(f"OCR error on page {i+1}: {str(ocr_error)}")
                                    continue
                            
                            if ocr_text.strip():
                                final_text = ocr_text
                                pdf_processed = True
                                print("✅ OCR processing successful")
                            else:
                                print("❌ OCR could not extract any text")
                                
                    except ImportError:
                        print("❌ OCR libraries not installed. Install with: pip install pytesseract pdf2image")
                    except Exception as ocr_error:
                        error_msg = str(ocr_error).lower()
                        if "tesseract" in error_msg:
                            print("❌ Tesseract OCR not installed or not in PATH")
                            summary = """🔧 **Tesseract OCR Required**

Your PDF is being processed with OCR, but Tesseract OCR engine is missing.

**Quick Installation (2 minutes):**

1. **Download Tesseract:**
   • Visit: https://github.com/UB-Mannheim/tesseract/wiki
   • Download: tesseract-ocr-w64-setup-5.4.0.20240606.exe

2. **Install:**
   • Run the installer
   • Choose installation path: C:\\Program Files\\Tesseract-OCR
   • Check "Add Tesseract to PATH" during installation

3. **Restart Server:**
   • Stop Django server (Ctrl+C)
   • Restart: python manage.py runserver

4. **Try Again:**
   • Upload your PDF and click "Generate Smart Summary"

**Alternative:** Use the "Test with Sample" button to verify text processing works.

**Current Status:** ✅ Poppler installed | ❌ Tesseract needed"""
                        else:
                            print(f"❌ OCR processing failed: {str(ocr_error)}")
                            summary = f"OCR processing failed: {str(ocr_error)}. The PDF might be corrupted or contain complex images."
                    
            except Exception as e:
                print(f"❌ PDF processing error: {str(e)}")
                print(f"Error type: {type(e).__name__}")
                import traceback
                print("Full traceback:")
                traceback.print_exc()
                
                # More specific error messages
                error_msg = str(e).lower()
                if "password" in error_msg or "encrypted" in error_msg:
                    summary = "PDF is password-protected. Please remove the password protection and try again."
                elif "damaged" in error_msg or "corrupt" in error_msg or "invalid" in error_msg:
                    summary = "PDF file appears to be corrupted or damaged. Please try a different file."
                elif "not a pdf" in error_msg or "invalid pdf" in error_msg:
                    summary = "The uploaded file is not a valid PDF. Please ensure you're uploading a PDF document."
                else:
                    summary = f"PDF processing failed: {str(e)}. Please try a different PDF or paste your notes manually."

        # If PDF didn't work, use notes field
        if not pdf_processed and not final_text:
            print("Using notes field as fallback")
            final_text = notes
            print(f"Notes text length: {len(final_text)} characters")

        # Check if extracted text is too short (likely scanned PDF)
        extracted_text = final_text.strip()
        if not extracted_text or len(extracted_text) < 50:
            print("❌ Text extraction failed or too short - likely scanned PDF")
            return render(request, 'ai/smart_notes.html', {
                'error': 'Could not extract text from this PDF. '
                         'Please upload a text-based PDF, not a scanned image. '
                         'Try copy-pasting your notes in the text box instead.',
                'summary': None
            })

        if not final_text.strip():
            print("❌ No text content available for summarization")
            if pdf_file and not pdf_processed:
                summary = "PDF could not be processed. The file might be: 1) Scanned images (no text), 2) Password-protected, 3) Corrupted, or 4) Contains only images. Try converting the PDF to text using Adobe Acrobat or an online OCR tool, then paste the text here."
            else:
                summary = "Please paste notes or upload a PDF."
        else:
            print(f"✅ Proceeding with summarization, text length: {len(final_text)}")
            # Limit text to avoid API limits
            if len(final_text) > 8000:
                final_text = final_text[:8000] + "\n\n[Note: Text was truncated for processing]"
                print("Text truncated to 8000 characters")
            
            prompt = f"""
Summarize this into exam-ready study notes:

{final_text}
"""

            try:
                content, error = call_groq(prompt, max_tokens=800)
                
                if error:
                    print(f"Groq Error: {error}")
                    summary = f"AI summarization failed: {error}"
                else:
                    summary = content
                    print("✅ AI summarization successful")
                    
                    # Record study activity
                    StudyActivity.objects.create(
                        user=request.user,
                        activity_type='smart_notes',
                        duration_minutes=15
                    )
                    
                    # Update mastery progress
                    mastery, created = MasteryProgress.objects.get_or_create(
                        user=request.user,
                        subject='General',
                        topic='Smart Notes',
                        defaults={'mastery_level': 10.0}
                    )
                    if not created:
                        mastery.mastery_level = min(mastery.mastery_level + 5, 100)
                        mastery.study_sessions += 1
                        mastery.save()
                    
            except Exception as api_error:
                print(f"❌ API request failed: {str(api_error)}")
                summary = f"Failed to generate summary: {str(api_error)}"

        print("=== SMART NOTES DEBUG END ===")
        print(f"Final summary length: {len(summary) if summary else 0} characters")

    return render(request, "ai/smart_notes.html", {"summary": summary})

@login_required
def planner_simple(request):
    """Simple test view for Study Planner"""
    plans = StudyPlan.objects.filter(user=request.user)
    return render(request, "ai/planner_simple.html", {
        'plans': plans
    })

@login_required
def planner_test(request):
    """Test view for Study Planner visibility"""
    return render(request, "ai/planner_test.html", {
        'plans': StudyPlan.objects.filter(user=request.user)
    })

@login_required
def planner(request):
    """Study Planner main page"""
    plans = StudyPlan.objects.filter(user=request.user)
    
    context = {
        'plans': plans,
    }
    return render(request, "ai/planner.html", context)

@login_required
def create_plan(request):
    """Create new study plan"""
    if request.method == 'POST':
        try:
            # Get form data
            title = request.POST.get('title')
            exam_date = request.POST.get('exam_date')
            hours_per_day = int(request.POST.get('hours_per_day'))
            
            # Create study plan
            plan = StudyPlan.objects.create(
                user=request.user,
                title=title,
                exam_date=exam_date,
                total_study_hours_per_day=hours_per_day
            )
            
            # Add subjects
            subjects_data = request.POST.getlist('subjects')
            difficulties = request.POST.getlist('difficulties')
            
            for i, subject_name in enumerate(subjects_data):
                if subject_name.strip():
                    PlanSubject.objects.create(
                        plan=plan,
                        subject_name=subject_name.strip(),
                        difficulty=difficulties[i] if i < len(difficulties) else 'medium'
                    )
            
            # Generate AI schedule
            subjects_list = [
                {
                    'name': subject.subject_name,
                    'difficulty': subject.difficulty
                }
                for subject in plan.plansubject_set.all()
            ]
            
            ai_schedule = generate_study_schedule(exam_date, hours_per_day, subjects_list)
            
            if ai_schedule:
                plan.ai_schedule = ai_schedule
                plan.save()
                
                # Create study sessions from AI schedule
                create_study_sessions(plan, ai_schedule)
                
                return JsonResponse({
                    'success': True,
                    'plan_id': plan.id,
                    'message': 'Study plan created successfully!'
                })
            else:
                # Generate fallback schedule
                fallback_schedule = generate_fallback_schedule(exam_date, hours_per_day, subjects_list)
                if fallback_schedule:
                    plan.ai_schedule = fallback_schedule
                    plan.save()
                    
                    # Create study sessions from fallback schedule
                    create_study_sessions(plan, fallback_schedule)
                    
                    return JsonResponse({
                        'success': True,
                        'plan_id': plan.id,
                        'message': 'Study plan created with basic schedule!'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Failed to generate AI schedule. Please try again.'
                    })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return render(request, "ai/create_plan.html")

@login_required
def plan_detail(request, plan_id):
    """Study plan detail page"""
    plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
    subjects = plan.plansubject_set.all()
    sessions = StudySession.objects.filter(plan=plan)
    
    # Get today's sessions
    today = timezone.now().date()
    today_sessions = sessions.filter(date=today)
    
    # Pre-process schedule data
    schedule = []
    unique_dates = sessions.dates('date', 'day').order_by('date')
    for session_date in unique_dates:
        day_sessions = sessions.filter(date=session_date)
        schedule.append({
            'date': session_date,
            'date_display': session_date.strftime('%A, %B %d, %Y'),
            'is_today': session_date == today,
            'is_past': session_date < today,
            'sessions': day_sessions
        })
    
    # Calculate progress metrics
    completed_sessions = sessions.filter(status='completed').count()
    completion_percentage = int((completed_sessions / plan.total_sessions * 100) if plan.total_sessions > 0 else 0)
    
    # Get current week sessions
    current_week = get_current_week_sessions(today, sessions)
    
    context = {
        'plan': plan,
        'subjects': subjects,
        'sessions': sessions,
        'today_sessions': today_sessions,
        'current_week': current_week,
        'schedule': schedule,
        'today': today,
    }
    return render(request, "ai/plan_detail.html", context)

@login_required
@require_POST
def mark_session_complete(request, session_id):
    """Mark study session as completed"""
    session = get_object_or_404(StudySession, id=session_id, plan__user=request.user)
    session.status = 'completed'
    session.save()
    
    # Update progress
    progress, created = StudyProgress.objects.get_or_create(
        plan=session.plan,
        subject=session.subject
    )
    progress.update_progress()
    
    return JsonResponse({
        'success': True,
        'message': 'Session marked as completed!'
    })

@login_required
@require_POST
def skip_session(request, session_id):
    """Skip study session"""
    session = get_object_or_404(StudySession, id=session_id, plan__user=request.user)
    session.status = 'skipped'
    session.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Session skipped!'
    })

@login_required
@require_POST
def delete_plan(request, plan_id):
    """Delete study plan"""
    plan = get_object_or_404(StudyPlan, id=plan_id, user=request.user)
    plan.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Study plan deleted!'
    })

def generate_study_schedule(exam_date, hours_per_day, subjects):
    """Generate AI-powered study schedule"""
    try:
        from django.conf import settings
        import requests
        import json
        from datetime import datetime, timedelta
        
        # Prepare subjects list
        subjects_list = []
        for subject in subjects:
            subjects_list.append(subject['name'] if 'name' in subject else str(subject))
        
        subjects_str = ", ".join(subjects_list)
        
        # Simplified prompt
        prompt = f"""Create a study schedule for a student with these subjects: {subjects_str}. 
Exam date: {exam_date}, Study hours per day: {hours_per_day}.
Return JSON with this exact structure:
{
  "plan_summary": "Create a {len(subjects)}-subject study schedule",
  "daily_schedule": [
    {"day": 1, "date": "2024-03-01", "sessions": []},
    {"day": 2, "date": "2024-03-02", "sessions": []}
  ]
}
Return only valid JSON."""
        
        content, error = call_groq(prompt, max_tokens=1000)
        
        if error:
            print(f"Groq Error: {error}")
            return None
            
        # Strip markdown and clean response
        raw = content.strip()
        if raw.startswith('```'):
            raw = raw.split('```')[1]
            if raw.startswith('json'):
                raw = raw[4:].strip()
        raw = raw.replace('```', '').strip()
        
        # Try to parse JSON
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"AI schedule parsing error: {e}")
            print(f"Raw AI response: {content}")
            print(f"Cleaned response: {raw}")
            return None
        
    except Exception as e:
        print(f"AI schedule generation error: {e}")
        return None

def create_study_sessions(plan, ai_schedule):
    """Create study sessions from AI schedule"""
    from datetime import datetime, timedelta
    
    try:
        daily_schedule = ai_schedule.get('daily_schedule', [])
        subjects_dict = {s.subject_name: s for s in plan.plansubject_set.all()}
        
        for day_data in daily_schedule:
            date_str = day_data.get('date')
            sessions = day_data.get('sessions', [])
            
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                continue
            
            current_time = datetime.strptime('09:00', '%H:%M').time()  # Start at 9 AM
            
            for session_data in sessions:
                subject_name = session_data.get('subject')
                subject = subjects_dict.get(subject_name)
                
                if subject:
                    duration = session_data.get('duration_minutes', 60)
                    
                    # Calculate end time
                    start_datetime = datetime.combine(date_obj, current_time)
                    end_datetime = start_datetime + timedelta(minutes=duration)
                    end_time = end_datetime.time()
                    
                    StudySession.objects.create(
                        plan=plan,
                        subject=subject,
                        date=date_obj,
                        start_time=current_time,
                        end_time=end_time,
                        duration_minutes=duration,
                        session_type=session_data.get('session_type', 'theory'),
                        topic_focus=session_data.get('topic_focus', ''),
                        tips=session_data.get('tips', '')
                    )
                    
                    # Update current time for next session
                    current_time = end_time
                    
                    # Add 15-minute break between sessions
                    break_time = datetime.combine(date_obj, current_time) + timedelta(minutes=15)
                    current_time = break_time.time()
                    
                    # Don't schedule after 9 PM
                    if current_time.hour >= 21:
                        break
                        
    except Exception as e:
        print(f"Error creating study sessions: {e}")

def generate_fallback_schedule(exam_date, hours_per_day, subjects):
    """Generate basic rule-based study schedule as fallback"""
    from datetime import datetime, timedelta
    import json
    
    try:
        exam_date_obj = datetime.strptime(exam_date, '%Y-%m-%d').date()
        days_until_exam = (exam_date_obj - datetime.now().date()).days
        
        if days_until_exam <= 0:
            days_until_exam = 30  # Default to 30 days
        
        # Calculate total study days
        total_study_days = max(days_until_exam - 2, 20)  # Reserve last 2 days for revision
        
        # Divide study time among subjects
        num_subjects = len(subjects)
        if num_subjects == 0:
            return None
            
        # Basic schedule structure
        daily_schedule = []
        current_date = datetime.now().date()
        
        for day in range(min(total_study_days, 30)):
            study_date = current_date + timedelta(days=day)
            sessions = []
            
            # Create 2-3 study sessions per day
            sessions_per_day = min(3, max(2, num_subjects))
            
            start_time = datetime.strptime('09:00', '%H:%M').time()
            
            for i in range(sessions_per_day):
                subject_idx = i % num_subjects
                subject_name = subjects[subject_idx]['name'] if isinstance(subjects[subject_idx], dict) else str(subjects[subject_idx])
                
                session = {
                    'subject': subject_name,
                    'duration_minutes': 120,  # 2 hours per session
                    'session_type': 'theory' if i % 2 == 0 else 'practice',
                    'tips': f'Focus on {subject_name} fundamentals'
                }
                sessions.append(session)
                
                # Update start time for next session
                start_time = (datetime.combine(study_date, start_time) + timedelta(hours=2, minutes=30)).time()
            
            daily_schedule.append({
                'day': day + 1,
                'date': study_date.strftime('%Y-%m-%d'),
                'sessions': sessions
            })
        
        return {
            'plan_summary': f'Basic {num_subjects}-subject study schedule created',
            'daily_schedule': daily_schedule,
            'subject_breakdown': [
                {'subject': subj['name'] if isinstance(subj, dict) else str(subj), 'total_hours': 120, 'priority': 'medium'}
                for subj in subjects
            ],
            'study_tips': [
                'Study consistently for 2-3 hours daily',
                'Take 15-minute breaks between study sessions',
                'Focus on difficult subjects first',
                'Use last 2 days for comprehensive revision'
            ]
        }
        
    except Exception as e:
        print(f"Fallback schedule generation error: {e}")
        return None

def get_current_week_sessions(today, sessions):
    """Get sessions for current week"""
    from datetime import timedelta
    
    # Get start of week (Monday)
    start_of_week = today - timedelta(days=today.weekday())
    
    # Get all sessions for this week
    week_sessions = []
    for i in range(7):
        date = start_of_week + timedelta(days=i)
        day_sessions = sessions.filter(date=date)
        week_sessions.append({
            'date': date,
            'sessions': day_sessions,
            'is_today': date == today,
            'day_name': date.strftime('%A')
        })
    
    return week_sessions

@login_required
def career_test(request):
    """Test endpoint for career API"""
    import json
    import requests
    import os
    from django.http import JsonResponse
    
    try:
        # Debug environment variables
        env_vars = {
            'GROQ_API_KEY': bool(settings.GROQ_API_KEY),
            'DJANGO_SETTINGS_MODULE': os.getenv('DJANGO_SETTINGS_MODULE'),
            'DEBUG': os.getenv('DEBUG'),
            'all_env_keys': list(os.environ.keys())[:10]  # First 10 env vars
        }
        
        print(f"DEBUG: Environment check - {env_vars}")
        
        # Simple test request
        content, error = call_groq("Respond with: 'API Test Successful'", max_tokens=10)
        
        return JsonResponse({
            "status": "success",
            "api_key_available": bool(settings.GROQ_API_KEY),
            "api_response": content[:100] if content else str(error),
            "environment": env_vars
        })
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "error": str(e),
            "api_key_available": bool(settings.GROQ_API_KEY),
            "environment": {
                'GROQ_API_KEY': bool(settings.GROQ_API_KEY),
                'DJANGO_SETTINGS_MODULE': os.getenv('DJANGO_SETTINGS_MODULE')
            }
        })

@login_required
def career_simple_test(request):
    """Simple test endpoint without AI dependency"""
    from django.http import JsonResponse
    
    # Test data to verify template rendering
    test_careers = [
        {
            "title": "Software Engineer",
            "field": "Information Technology",
            "description": "Design and develop software applications for various industries.",
            "match_percentage": 92,
            "avg_salary": "₹8 LPA - ₹25 LPA",
            "growth": "High",
            "skills": ["Python", "JavaScript", "React", "Node.js", "SQL"],
            "job_outlook": "Excellent demand with remote work opportunities.",
            "industries": ["IT Services", "FinTech", "E-commerce", "Healthcare"],
            "career_steps": [
                {"step": 1, "title": "Learn Programming", "description": "Master coding fundamentals", "duration": "1 year"},
                {"step": 2, "title": "Build Projects", "description": "Create portfolio projects", "duration": "1 year"},
                {"step": 3, "title": "Get Internship", "description": "Gain industry experience", "duration": "6 months"},
                {"step": 4, "title": "Entry Level Job", "description": "Start as junior developer", "duration": "2 years"},
                {"step": 5, "title": "Senior Developer", "description": "Lead development teams", "duration": "3 years"},
                {"step": 6, "title": "Tech Lead", "description": "Manage technical strategy", "duration": "4 years"}
            ]
        }
    ]
    
    return render(request, "ai/career.html", {
        'careers': test_careers,
        'selected_stream': 'Computer Science',
        'error_message': None
    })

@login_required
def career(request):
    from django.conf import settings
    import json
    
    if request.method == 'POST':
        stream = request.POST.get('stream', '').strip()
        
        if not stream:
            return render(request, 'ai/career.html', {
                'error': 'Please enter your academic stream'
            })
        
        # Debug
        print(f"=== CAREER GUIDE DEBUG ===")
        print(f"Stream: {stream}")
        print(f"Groq Key exists: {bool(settings.GROQ_API_KEY)}")
        
        if not settings.GROQ_API_KEY:
            return render(request, 'ai/career.html', {
                'error': 'Groq API key not configured. Please contact admin.',
                'stream': stream
            })
        
        prompt = f"""You are an expert career counselor for Indian students.
A student studying {stream} wants detailed career guidance.

Generate exactly 6 detailed career paths for {stream} students in India.

Return ONLY a valid JSON array with NO markdown, NO extra text:
[
  {{
    "title": "Software Engineer",
    "icon": "💻",
    "description": "Design, develop and maintain software applications and systems for companies across all industries",
    "avg_salary": "6-40 LPA",
    "starting_salary": "4-8 LPA",
    "senior_salary": "25-60 LPA",
    "growth": "Excellent",
    "demand": "Very High",
    "work_type": "Office/Remote",
    "skills": ["Python", "Java", "Data Structures", "Problem Solving", "Git", "SQL"],
    "soft_skills": ["Communication", "Teamwork", "Problem Solving"],
    "companies": ["Google", "Microsoft", "TCS", "Infosys", "Wipro", "Startups"],
    "top_roles": ["Backend Developer", "Frontend Developer", "Full Stack Developer"],
    "certifications": ["AWS Certified", "Google Cloud", "Oracle Java"],
    "education": ["B.Tech/B.E in CS/IT", "MCA", "BCA + MCA"],
    "steps": [
      "Complete your degree with good CGPA",
      "Learn core programming languages",
      "Build 3-4 strong projects for portfolio",
      "Contribute to open source",
      "Clear DSA interviews",
      "Apply to product and service companies"
    ],
    "pros": ["High salary", "Remote work possible", "Global opportunities"],
    "cons": ["Competitive field", "Continuous learning required"],
    "future": "AI and cloud will create more opportunities. Demand will grow 25% by 2030."
  }}
]

Generate 6 such detailed careers specifically for {stream} students.
Make salaries realistic for Indian market in LPA.
Make companies relevant to India.
Return ONLY the JSON array, absolutely no other text."""

        content, error = call_groq(prompt, max_tokens=3000)
        if error:
            return render(request, 'ai/career.html', {
                'error': f'AI Error: {error}',
                'stream': stream
            })

        # Parse JSON
        try:
            content = content.replace('```json', '').replace('```', '').strip()
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end > start:
                content = content[start:end]
            careers = json.loads(content)
            return render(request, 'ai/career.html', {
                'careers': careers,
                'stream': stream,
                'error': None
            })
        except json.JSONDecodeError as e:
            return render(request, 'ai/career.html', {
                'error': 'Failed to parse response. Please try again.',
                'stream': stream
            })
    
    return render(request, 'ai/career.html', {})

# ... (rest of the code remains the same)

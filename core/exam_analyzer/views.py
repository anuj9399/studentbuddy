from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
import os
import pypdf
import pytesseract
from PIL import Image
try:
    import pdf2image
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
import requests
from dotenv import load_dotenv
from .models import ExamSubject, QuestionPaper, ExamAnalysis

load_dotenv()

@login_required
def analyzer_home(request):
    """Main exam analyzer page with list of subjects"""
    subjects = ExamSubject.objects.filter(user=request.user)
    
    context = {
        'subjects': subjects,
    }
    return render(request, 'exam_analyzer/analyzer_home.html', context)

@login_required
def create_subject(request):
    """Create a new subject"""
    if request.method == 'POST':
        subject_name = request.POST.get('subject_name')
        if subject_name:
            subject = ExamSubject.objects.create(
                user=request.user,
                subject_name=subject_name
            )
            messages.success(request, f'Subject "{subject_name}" created successfully!')
            return redirect('exam_analyzer:upload_papers', subject_id=subject.id)
        else:
            messages.error(request, 'Please enter a subject name')
    
    return render(request, 'exam_analyzer/create_subject.html')

@login_required
def upload_papers(request, subject_id):
    """Upload question papers for a subject"""
    subject = get_object_or_404(ExamSubject, id=subject_id, user=request.user)
    papers = QuestionPaper.objects.filter(subject=subject)
    
    if request.method == 'POST':
        # Handle file uploads
        files = request.FILES.getlist('pdf_files')
        years = request.POST.getlist('years')
        
        uploaded_count = 0
        error_messages = []
        
        for i, file in enumerate(files):
            year = years[i] if i < len(years) else None
            
            # Validate file
            if not file.name.lower().endswith('.pdf'):
                error_messages.append(f"'{file.name}' is not a PDF file")
                continue
                
            if not year:
                error_messages.append(f"'{file.name}' - Year is required")
                continue
                
            try:
                year = int(year)
                if year < 2000 or year > 2030:
                    error_messages.append(f"'{file.name}' - Invalid year: {year}")
                    continue
            except ValueError:
                error_messages.append(f"'{file.name}' - Year must be a number")
                continue
            
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                error_messages.append(f"'{file.name}' - File too large (max 10MB)")
                continue
            
            try:
                paper = QuestionPaper.objects.create(
                    subject=subject,
                    file=file,
                    year=year
                )
                
                # Extract text from PDF
                extracted_text = extract_text_from_pdf(paper.file.path)
                paper.extracted_text = extracted_text
                paper.save()
                uploaded_count += 1
                
            except Exception as e:
                error_messages.append(f"'{file.name}' - Upload failed: {str(e)}")
                continue
        
        if uploaded_count > 0:
            # Update subject paper count
            subject.total_papers_uploaded = QuestionPaper.objects.filter(subject=subject).count()
            subject.save()
            
            success_message = f'{uploaded_count} papers uploaded successfully!'
            if error_messages:
                success_message += f' (Some files had errors: "; ".join(error_messages))'
            messages.success(request, success_message)
        else:
            if error_messages:
                messages.error(request, f'Upload failed: "; ".join(error_messages)')
            else:
                messages.error(request, 'No valid PDF files were uploaded')
        
        return redirect('exam_analyzer:upload_papers', subject_id=subject.id)
    
    context = {
        'subject': subject,
        'papers': papers,
    }
    return render(request, 'exam_analyzer/upload_papers.html', context)

@login_required
@require_POST
def run_analysis(request, subject_id):
    """Run AI analysis on uploaded papers"""
    subject = get_object_or_404(ExamSubject, id=subject_id, user=request.user)
    papers = QuestionPaper.objects.filter(subject=subject)
    
    print(f"Starting analysis for subject: {subject.subject_name}")
    print(f"Number of papers: {papers.count()}")
    
    if papers.count() < 2:
        return JsonResponse({
            'success': False, 
            'message': 'Please upload at least 2 question papers for analysis'
        })
    
    # Check if papers have extracted text
    papers_with_text = papers.filter(extracted_text__isnull=False).exclude(extracted_text='')
    print(f"Papers with extracted text: {papers_with_text.count()}")
    
    if papers_with_text.count() < 2:
        return JsonResponse({
            'success': False, 
            'message': 'Not enough text could be extracted from the uploaded papers. Please try uploading clearer PDF files.'
        })
    
    try:
        # Combine all extracted text
        combined_text = '\n\n'.join([paper.extracted_text for paper in papers_with_text])
        print(f"Combined text length: {len(combined_text)} characters")
        
        if not combined_text.strip():
            return JsonResponse({
                'success': False, 
                'message': 'No text could be extracted from the uploaded papers'
            })
        
        # Analyze with AI
        print("Starting AI analysis...")
        ai_data = analyze_with_ai(combined_text)
        
        if ai_data:
            print("✅ AI analysis successful")
            
            # Add percentage calculation to most_repeated_topics
            most_repeated_topics = ai_data.get('most_repeated_topics', [])
            for topic in most_repeated_topics:
                if topic.get('appeared_in') and topic.get('total_papers'):
                    topic['percentage'] = (topic['appeared_in'] / topic['total_papers']) * 100
            
            # Create analysis record
            analysis = ExamAnalysis.objects.create(
                subject=subject,
                most_repeated_topics=most_repeated_topics,
                high_probability_topics=ai_data.get('high_probability_topics', []),
                chapter_weightage=ai_data.get('chapter_weightage', []),
                question_pattern=ai_data.get('question_pattern', {}),
                predicted_questions=ai_data.get('predicted_questions', []),
                study_priority_list=ai_data.get('study_priority_list', []),
                quick_insights=ai_data.get('quick_insights', []),
                raw_ai_response=json.dumps(ai_data)
            )
            
            print(f"✅ Analysis saved with ID: {analysis.id}")
            
            return JsonResponse({
                'success': True, 
                'message': 'Analysis completed successfully!',
                'analysis_id': analysis.id
            })
        else:
            print("❌ AI analysis returned None")
            return JsonResponse({
                'success': False, 
                'message': 'AI analysis failed. The AI service might be unavailable or the content might not be suitable for analysis. Please try again or check the server logs for details.'
            })
            
    except Exception as e:
        print(f"❌ Analysis failed with exception: {str(e)}")
        return JsonResponse({
            'success': False, 
            'message': f'Analysis failed: {str(e)}'
        })

@login_required
def analysis_results(request, subject_id):
    """Show analysis results for a subject"""
    subject = get_object_or_404(ExamSubject, id=subject_id, user=request.user)
    analysis = subject.latest_analysis
    
    if not analysis:
        messages.info(request, 'No analysis available yet. Please upload papers and run analysis.')
        return redirect('exam_analyzer:upload_papers', subject_id=subject.id)
    
    context = {
        'subject': subject,
        'analysis': analysis,
        'papers_count': QuestionPaper.objects.filter(subject=subject).count(),
    }
    return render(request, 'exam_analyzer/analysis_results.html', context)

@login_required
@require_POST
def delete_paper(request, paper_id):
    """Delete a question paper"""
    paper = get_object_or_404(QuestionPaper, id=paper_id, subject__user=request.user)
    subject = paper.subject
    
    # Delete file
    if paper.file and os.path.exists(paper.file.path):
        os.remove(paper.file.path)
    
    paper.delete()
    
    # Update subject paper count
    subject.total_papers_uploaded = QuestionPaper.objects.filter(subject=subject).count()
    subject.save()
    
    return JsonResponse({'success': True, 'message': 'Paper deleted successfully'})

@login_required
@require_POST
def delete_subject(request, subject_id):
    """Delete a subject and all related data"""
    subject = get_object_or_404(ExamSubject, id=subject_id, user=request.user)
    
    # Delete all papers and their files
    for paper in subject.questionpaper_set.all():
        if paper.file and os.path.exists(paper.file.path):
            os.remove(paper.file.path)
        paper.delete()
    
    subject.delete()
    
    return JsonResponse({'success': True, 'message': 'Subject deleted successfully'})

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pypdf, fallback to OCR if needed"""
    try:
        # First try pypdf
        with open(pdf_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            text = ""
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    text += page_text + "\n"
                except Exception as e:
                    print(f"Error extracting text from page {page_num}: {e}")
                    continue
            
            if text.strip():
                print(f"Successfully extracted {len(text)} characters using pypdf")
                return text
            else:
                print("pypdf extracted empty text, trying OCR")
                
    except Exception as e:
        print(f"pypdf extraction failed: {e}")
    
    try:
        # Fallback to OCR
        print("Attempting OCR extraction...")
        if PDF2IMAGE_AVAILABLE:
            images = pdf2image.convert_from_path(pdf_path, dpi=200)
            text = ""
            for i, image in enumerate(images):
                try:
                    page_text = pytesseract.image_to_string(image)
                    text += page_text + "\n"
                    print(f"OCR processed page {i+1}/{len(images)}")
                except Exception as e:
                    print(f"OCR failed on page {i+1}: {e}")
                    continue
        else:
            print("pdf2image not available - skipping OCR")
            text = ""
        
        if text.strip():
            print(f"Successfully extracted {len(text)} characters using OCR")
            return text
        else:
            print("OCR extracted empty text")
            
    except Exception as e:
        print(f"OCR extraction failed: {e}")
    
    print(f"Failed to extract any text from {pdf_path}")
    return ""

def analyze_with_ai(content):
    """Analyze content with AI"""
    try:
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            print("ERROR: OPENROUTER_API_KEY not found in environment variables")
            return None
        
        print(f"Starting AI analysis with content length: {len(content)} characters")
        
        prompt = f"""You are an expert exam pattern analyzer. Analyze the following previous year question papers and return a JSON response with this exact structure:
{{
  most_repeated_topics: [{{topic: string, appeared_in: number, total_papers: number, importance: high/medium/low}}],
  high_probability_topics: [{{topic: string, reason: string, confidence: high/medium/low}}],
  chapter_weightage: [{{chapter: string, marks_percentage: number, frequency: number}}],
  question_pattern: {{theory_percentage: number, numerical_percentage: number, diagram_percentage: number, short_questions: number, long_questions: number, average_total_marks: number}},
  predicted_questions: [{{question: string, topic: string, likelihood: high/medium/low, marks: number}}],
  study_priority_list: [{{rank: number, topic: string, reason: string, estimated_study_hours: number}}],
  quick_insights: [list of 5 short powerful insight strings]
}}
Return only valid JSON, nothing else.
Papers content: {content[:4000]}"""  # Limit content to avoid token limits
        
        print("Sending request to OpenRouter API...")
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://studentbuddy-v5ah.onrender.com",
                "X-Title": "StudentBuddy",
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 3000,
                "temperature": 0.3,
            },
            timeout=30
        )
        
        print(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f"Raw AI response: {content[:200]}...")
            
            # Try to parse JSON
            try:
                result = json.loads(content)
                print("✅ Successfully parsed JSON response")
                return result
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                # Extract JSON from response if it's wrapped in code blocks
                if '```json' in content:
                    json_str = content.split('```json')[1].split('```')[0].strip()
                    print("Trying to parse JSON from code blocks...")
                    try:
                        result = json.loads(json_str)
                        print("✅ Successfully parsed JSON from code blocks")
                        return result
                    except json.JSONDecodeError as e2:
                        print(f"JSON from code blocks also failed: {e2}")
                else:
                    print("No JSON code blocks found in response")
                return None
        else:
            print(f"API request failed with status {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("ERROR: AI request timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR: AI request failed: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error in AI analysis: {e}")
        return None

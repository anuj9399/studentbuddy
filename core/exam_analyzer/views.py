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
import pdf2image
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
        for i, file in enumerate(files):
            year = years[i] if i < len(years) else None
            if year and file.name.lower().endswith('.pdf'):
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
        
        if uploaded_count > 0:
            # Update subject paper count
            subject.total_papers_uploaded = QuestionPaper.objects.filter(subject=subject).count()
            subject.save()
            messages.success(request, f'{uploaded_count} papers uploaded successfully!')
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
    
    if papers.count() < 2:
        return JsonResponse({
            'success': False, 
            'message': 'Please upload at least 2 question papers for analysis'
        })
    
    try:
        # Combine all extracted text
        combined_text = '\n\n'.join([paper.extracted_text for paper in papers if paper.extracted_text])
        
        if not combined_text.strip():
            return JsonResponse({
                'success': False, 
                'message': 'No text could be extracted from the uploaded papers'
            })
        
        # Analyze with AI
        ai_data = analyze_with_ai(combined_text)
        
        if ai_data:
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
            
            return JsonResponse({
                'success': True, 
                'message': 'Analysis completed successfully!',
                'analysis_id': analysis.id
            })
        else:
            return JsonResponse({
                'success': False, 
                'message': 'AI analysis failed. Please try again.'
            })
            
    except Exception as e:
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
            for page in reader.pages:
                text += page.extract_text()
            
            if text.strip():
                return text
    except Exception as e:
        print(f"pypdf extraction failed: {e}")
    
    try:
        # Fallback to OCR
        images = pdf2image.convert_from_path(pdf_path)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image)
        
        return text
    except Exception as e:
        print(f"OCR extraction failed: {e}")
        return ""

def analyze_with_ai(content):
    """Analyze content with AI"""
    try:
        api_key = os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            return None
        
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
Papers content: {content}"""
        
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 3000,
                "temperature": 0.3,
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            # Try to parse JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Extract JSON from response if it's wrapped in code blocks
                if '```json' in content:
                    json_str = content.split('```json')[1].split('```')[0].strip()
                    return json.loads(json_str)
                return None
        else:
            return None
            
    except Exception as e:
        print(f"AI analysis error: {e}")
        return None

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import requests

from .models import AcademicProfile, Semester

@login_required
def grade_setup(request):
    """First time setup with AI analysis"""
    try:
        request.user.academicprofile
        return redirect('grade_tracker:grade_dashboard')
    except AcademicProfile.DoesNotExist:
        pass
    
    if request.method == 'POST':
        try:
            # Create academic profile
            profile = AcademicProfile.objects.create(
                user=request.user,
                university_name=request.POST.get('university_name'),
                university_short=request.POST.get('university_short'),
                pattern_year=request.POST.get('pattern_year'),
                stream=request.POST.get('stream'),
                branch=request.POST.get('branch'),
                grading_scale=request.POST.get('grading_scale'),
                total_semesters=int(request.POST.get('total_semesters')),
            )
            
            # Get AI analysis
            ai_prompt = f"""You are an academic advisor. A student studies at {profile.university_name} ({profile.pattern_year} pattern), 
branch: {profile.branch}, stream: {profile.stream}, grading scale: {profile.grading_scale}.
Give a JSON response with this exact structure:
{{
    "minimum_cgpa": number (minimum CGPA considered passing at this university),
    "good_cgpa": number (CGPA considered good for placements at this university),
    "excellent_cgpa": number (CGPA considered excellent/distinction),
    "placement_cutoff": number (minimum CGPA most companies ask for campus placement),
    "university_info": string (2-3 lines about this university and its grading reputation),
    "pattern_info": string (what is pattern year means for this student),
    "benchmark_message": string (personalized advice like 'At SPPU 2019 pattern, scoring above 7.5 CGPA puts you in top 30% of students and qualifies you for most campus placements'),
    "improvement_tips": [list of 4 specific tips for this university/branch]
}}
Return only valid JSON."""
            
            # Call AI API
            try:
                from django.conf import settings
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://studentbuddy-v5ah.onrender.com",
                        "X-Title": "StudentBuddy",
                    },
                    json={
                        "model": "openai/gpt-4o-mini",
                        "messages": [{"role": "user", "content": ai_prompt}]
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    ai_data = response.json()
                    ai_response = ai_data['choices'][0]['message']['content']
                    
                    # Try to parse JSON response
                    try:
                        ai_parsed = json.loads(ai_response)
                        print(f"AI response parsed successfully: {ai_parsed}")
                    except json.JSONDecodeError as e:
                        print(f"AI JSON parsing error: {e}")
                        print(f"Raw AI response: {ai_response}")
                        # Use fallback values for SPPU Engineering 10.0 scale
                        ai_parsed = {
                            'minimum_cgpa': 5.0,
                            'good_cgpa': 7.0,
                            'excellent_cgpa': 9.0,
                            'placement_cutoff': 6.5,
                            'university_info': f"{profile.university_name} is one of the premier engineering universities in Maharashtra, known for its rigorous curriculum and industry connections.",
                            'pattern_info': f"The {profile.pattern_year} pattern follows the revised credit system and outcome-based evaluation framework.",
                            'benchmark_message': f"At {profile.university_short}, scoring above 7.5 CGPA puts you in the top 30% of students and qualifies you for most campus placements.",
                            'improvement_tips': [
                                "Focus on core subjects like Mathematics, Programming, and Data Structures as they have higher weightage",
                                "Maintain consistent attendance and regular study schedules to build strong fundamentals",
                                "Practice previous year question papers and understand exam patterns",
                                "Join technical clubs and participate in hackathons to build practical skills"
                            ]
                        }
                    
                    # Save individual fields
                    profile.minimum_cgpa = ai_parsed.get('minimum_cgpa', 5.0)
                    profile.good_cgpa = ai_parsed.get('good_cgpa', 7.0)
                    profile.excellent_cgpa = ai_parsed.get('excellent_cgpa', 9.0)
                    profile.placement_cutoff = ai_parsed.get('placement_cutoff', 6.5)
                    profile.university_info = ai_parsed.get('university_info', '')
                    profile.pattern_info = ai_parsed.get('pattern_info', '')
                    profile.benchmark_message = ai_parsed.get('benchmark_message', '')
                    profile.improvement_tips = json.dumps(ai_parsed.get('improvement_tips', []))
                    
                    # Also save raw AI analysis for backup
                    profile.ai_analysis = ai_response
                    profile.save()
                    
                    messages.success(request, 'University setup completed! AI analysis generated.')
                    return redirect('grade_tracker:grade_dashboard')
                    
            except Exception as e:
                print(f"AI API error: {e}")
                messages.error(request, f'Error getting AI analysis: {e}')
                # Still save profile with fallback values
                profile.save()
                
        except Exception as e:
            messages.error(request, f'Error saving setup: {e}')
    
    return render(request, 'grade_tracker/setup.html')

@login_required
def grade_dashboard(request):
    """Main dashboard with all features"""
    # Check if user has academic profile
    try:
        profile = request.user.academicprofile
    except AcademicProfile.DoesNotExist:
        return redirect('grade_tracker:grade_setup')
    
    # Get all semesters
    semesters = Semester.objects.filter(user=request.user)
    
    # Calculate CGPA and stats
    total_credits = sum(sem.credits for sem in semesters)
    total_weighted_points = sum(sem.weighted_points for sem in semesters)
    current_cgpa = total_weighted_points / total_credits if total_credits > 0 else 0
    
    # Calculate percentage
    if profile.grading_scale == 10.0:
        percentage = current_cgpa * 9.5
    elif profile.grading_scale == 4.0:
        percentage = current_cgpa * 25
    else:  # 7.0 scale
        percentage = (current_cgpa / 7.0) * 100
    
    # AI Analysis data - now using direct model fields
    ai_data = {
        'minimum_cgpa': float(profile.minimum_cgpa),
        'good_cgpa': float(profile.good_cgpa),
        'excellent_cgpa': float(profile.excellent_cgpa),
        'placement_cutoff': float(profile.placement_cutoff),
        'university_info': profile.university_info,
        'pattern_info': profile.pattern_info,
        'benchmark_message': profile.benchmark_message,
        'improvement_tips': json.loads(profile.improvement_tips or '[]')
    }
    
    # AI Improvement advice
    ai_advice = {}
    try:
        ai_advice = json.loads(profile.ai_improvement_advice or '{}')
    except json.JSONDecodeError:
        ai_advice = {}
    except Exception:
        ai_advice = {}
    
    # Trend analysis
    cgpa_trend = "stable"
    if len(semesters) >= 2:
        recent_sgpa = float(semesters.last().sgpa)
        previous_sgpa = float(semesters[len(semesters)-2].sgpa)
        if recent_sgpa > previous_sgpa:
            cgpa_trend = "improving"
        elif recent_sgpa < previous_sgpa:
            cgpa_trend = "declining"
    
    # Best and worst semesters
    best_semester = max(semesters, key=lambda x: float(x.sgpa)) if semesters else None
    worst_semester = min(semesters, key=lambda x: float(x.sgpa)) if semesters else None
    
    # Calculate required SGPA for placement cutoff
    remaining_semesters = profile.total_semesters - len(semesters)
    required_sgpa_for_placement = 0
    placement_cutoff = ai_data.get('placement_cutoff', profile.good_cgpa)
    
    if current_cgpa < float(profile.placement_cutoff) and remaining_semesters > 0:
        target_weighted = float(profile.placement_cutoff) * (total_credits + remaining_semesters * 20)
        required_weighted = target_weighted - total_weighted_points
        required_sgpa_for_placement = required_weighted / (remaining_semesters * 20)
    
    # Calculate required SGPA for excellent
    required_sgpa_for_excellent = 0
    if current_cgpa < float(profile.excellent_cgpa) and remaining_semesters > 0:
        target_weighted = float(profile.excellent_cgpa) * (total_credits + remaining_semesters * 20)
        required_weighted = target_weighted - total_weighted_points
        required_sgpa_for_excellent = required_weighted / (remaining_semesters * 20)
    
    context = {
        'profile': profile,
        'semesters': semesters,
        'current_cgpa': current_cgpa,
        'percentage': percentage,
        'total_credits': total_credits,
        'ai_data': ai_data,
        'ai_advice': ai_advice,
        'cgpa_trend': cgpa_trend,
        'best_semester': best_semester,
        'worst_semester': worst_semester,
        'remaining_semesters': remaining_semesters,
        'required_sgpa_for_placement': required_sgpa_for_placement,
        'required_sgpa_for_excellent': required_sgpa_for_excellent,
        'status_badge': get_status_badge(current_cgpa, profile),
    }
    
    return render(request, 'grade_tracker/dashboard.html', context)

@login_required
@require_POST
def add_semester(request):
    """Add new semester via AJAX"""
    try:
        profile = request.user.academicprofile
        
        semester = Semester.objects.create(
            user=request.user,
            semester_number=int(request.POST.get('semester_number')),
            sgpa=float(request.POST.get('sgpa')),
            credits=int(request.POST.get('credits'))
        )
        
        # Clear AI advice cache when semester is added
        profile.ai_improvement_advice = None
        profile.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Semester added successfully!',
            'semester': {
                'id': semester.id,
                'number': semester.semester_number,
                'sgpa': float(semester.sgpa),
                'credits': semester.credits,
                'weighted_points': semester.weighted_points,
                'status_badge': semester.status_badge
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error adding semester: {e}'
        })

@login_required
@require_POST
def delete_semester(request, semester_id):
    """Delete semester"""
    try:
        semester = get_object_or_404(Semester, id=semester_id, user=request.user)
        semester.delete()
        messages.success(request, 'Semester deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting semester: {e}')
    
    return redirect('grade_tracker:grade_dashboard')

@login_required
def print_report(request):
    """Print-friendly report"""
    try:
        profile = request.user.academicprofile
        semesters = Semester.objects.filter(user=request.user)
        
        # Calculate CGPA
        total_credits = sum(sem.credits for sem in semesters)
        total_weighted_points = sum(sem.weighted_points for sem in semesters)
        current_cgpa = total_weighted_points / total_credits if total_credits > 0 else 0
        
        if profile.grading_scale == 10.0:
            percentage = current_cgpa * 9.5
        elif profile.grading_scale == 4.0:
            percentage = current_cgpa * 25
        else:
            percentage = (current_cgpa / 7.0) * 100
        
        context = {
            'profile': profile,
            'semesters': semesters,
            'current_cgpa': current_cgpa,
            'percentage': percentage,
            'total_credits': total_credits,
            'ai_data': json.loads(profile.ai_analysis or '{}'),
        }
        
        return render(request, 'grade_tracker/print_report.html', context)
        
    except AcademicProfile.DoesNotExist:
        return redirect('grade_tracker:grade_setup')

def get_ai_improvement_advice(profile, semesters, current_cgpa):
    """Get AI improvement advice with caching"""
    # Check if we have cached advice
    if profile.ai_improvement_advice:
        try:
            return json.loads(profile.ai_improvement_advice)
        except:
            pass
    
    # Generate new advice only if we have semesters
    if not semesters:
        return {}
    
    # Prepare semester data
    semester_data = []
    for sem in semesters:
        semester_data.append(f"Semester {sem.semester_number}: SGPA {sem.sgpa} ({sem.credits} credits)")
    semester_data_str = ", ".join(semester_data)
    
    # AI prompt for personalized advice
    placement_cutoff = 'N/A'
    try:
        ai_analysis_data = json.loads(profile.ai_analysis or '{}')
        placement_cutoff = ai_analysis_data.get('placement_cutoff', 'N/A')
    except:
        placement_cutoff = 'N/A'
    
    ai_prompt = f"""A student at {profile.university_name} ({profile.pattern_year} pattern), branch: {profile.branch}, grading scale: {profile.grading_scale}, has the following semester performance: {semester_data_str}. Their current CGPA is {current_cgpa:.2f}. The placement benchmark at this university is {placement_cutoff} CGPA.

Analyze their performance and return JSON:
{{
  "performance_summary": "string (2-3 lines honest assessment of their academic journey)",
  "main_problem": "string (identify the main issue - declining trend, inconsistency, low scores etc)",
  "specific_advice": ["list of 4 very specific actionable improvement tips tailored to their branch and university"],
  "next_semester_target": number (realistic SGPA target for next semester based on their history),
  "motivation_message": "string (short motivating message)"
}}
Return only valid JSON."""
    
    try:
        from django.conf import settings
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://studentbuddy-v5ah.onrender.com",
                "X-Title": "StudentBuddy",
            },
            json={
                "model": "openai/gpt-4o-mini",
                "messages": [{"role": "user", "content": ai_prompt}]
            },
            timeout=30
        )
        
        if response.status_code == 200:
            ai_data = response.json()
            advice = ai_data['choices'][0]['message']['content']
            
            # Cache the advice
            profile.ai_improvement_advice = advice
            profile.save()
            
            return json.loads(advice)
            
    except Exception as e:
        print(f"AI advice error: {e}")
        return {}

@login_required
def reanalyse_university(request):
    """Re-analyse university with AI"""
    try:
        profile = request.user.academicprofile
        
        # Get existing semesters for context
        semesters = Semester.objects.filter(user=request.user)
        
        # Prepare semester data
        semester_data = []
        for sem in semesters:
            semester_data.append(f"Semester {sem.semester_number}: SGPA {sem.sgpa} ({sem.credits} credits)")
        semester_data_str = ", ".join(semester_data)
        
        # Calculate current CGPA
        total_credits = sum(sem.credits for sem in semesters)
        total_weighted_points = sum(sem.sgpa * sem.credits for sem in semesters)
        current_cgpa = total_weighted_points / total_credits if total_credits > 0 else 0
        
        # AI prompt for personalized advice
        ai_prompt = f"""A student at {profile.university_name} ({profile.pattern_year} pattern), branch: {profile.branch}, grading scale: {profile.grading_scale}, has the following semester performance: {semester_data_str}. Their current CGPA is {current_cgpa:.2f}. The placement benchmark at this university is currently {profile.placement_cutoff} CGPA.

Re-analyze their performance and return JSON:
{{
  "performance_summary": "string (2-3 lines honest assessment of their academic journey)",
  "main_problem": "string (identify main issue - declining trend, inconsistency, low scores etc)",
  "specific_advice": ["list of 4 very specific actionable improvement tips tailored to their branch and university"],
  "next_semester_target": number (realistic SGPA target for next semester based on their history),
  "motivation_message": "string (short motivating message)"
}}
Return only valid JSON."""
        
        # Call AI API
        try:
            from django.conf import settings
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://studentbuddy-v5ah.onrender.com",
                    "X-Title": "StudentBuddy",
                },
                json={
                    "model": "openai/gpt-4o-mini",
                    "messages": [{"role": "user", "content": ai_prompt}]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                ai_data = response.json()
                ai_response = ai_data['choices'][0]['message']['content']
                
                # Try to parse JSON response
                try:
                    ai_parsed = json.loads(ai_response)
                    print(f"AI re-analysis response parsed successfully: {ai_parsed}")
                except json.JSONDecodeError as e:
                    print(f"AI re-analysis JSON parsing error: {e}")
                    print(f"Raw AI re-analysis response: {ai_response}")
                    # Use fallback values
                    ai_parsed = {
                        'performance_summary': "Your academic performance shows room for improvement.",
                        'main_problem': "Inconsistent grades across semesters",
                        'specific_advice': [
                            "Focus on maintaining consistent performance across all subjects",
                            "Develop better study habits and time management",
                            "Seek help from professors for difficult subjects",
                            "Practice regularly with mock tests"
                        ],
                        'next_semester_target': 7.5,
                        'motivation_message': "You have the potential to excel with dedicated effort!"
                    }
                
                # Update improvement advice
                profile.ai_improvement_advice = ai_response
                profile.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'University re-analysed successfully!'
                })
                
        except Exception as e:
            print(f"Re-analysis error: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Error re-analysing university: {e}'
            })
            
    except AcademicProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Please complete university setup first.'
        })

def get_status_badge(cgpa, profile):
    """Get status badge based on AI benchmarks"""
    if cgpa >= profile.excellent_cgpa:
        return {"text": "Excellent 🏆", "color": "green"}
    elif cgpa >= profile.good_cgpa:
        return {"text": "Good for Placements ✅", "color": "blue"}
    elif cgpa >= profile.minimum_cgpa:
        return {"text": "Needs Improvement ⚠️", "color": "yellow"}
    else:
        return {"text": "Critical - Immediate Action Needed 🚨", "color": "red"}

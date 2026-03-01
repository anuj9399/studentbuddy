from accounts.models import StudentProfile, Task, StudyActivity, MasteryProgress
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import datetime, timedelta

@login_required
def dashboard(request):
    # Get or create user profile
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    # Calculate Tasks Pending
    tasks_pending = Task.objects.filter(user=request.user, status='pending').count()
    
    # Calculate Study Streak
    current_streak = calculate_study_streak(request.user)
    profile.current_streak = current_streak
    profile.save()
    
    # Calculate Mastery Percentage
    mastery_percentage = calculate_mastery_percentage(request.user)
    profile.mastery_percentage = mastery_percentage
    profile.save()
    
    # Get recent activities for charts
    recent_tasks = Task.objects.filter(user=request.user).order_by('-created_at')[:7]
    study_activities = StudyActivity.objects.filter(user=request.user).order_by('-date')[:30]
    
    context = {
        'tasks_pending': tasks_pending,
        'study_streak': current_streak,
        'mastery_percentage': mastery_percentage,
        'recent_tasks': recent_tasks,
        'study_activities': study_activities,
        'profile': profile,
    }
    
    return render(request, "dashboard.html", context)

@login_required
def profile(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # Update User model fields
        request.user.first_name = request.POST.get("first_name", "")
        request.user.last_name = request.POST.get("last_name", "")
        request.user.email = request.POST.get("email")
        request.user.save()

        # Update Profile model fields
        profile.username = request.POST.get("username")
        profile.stream = request.POST.get("stream")
        profile.branch = request.POST.get("branch")
        profile.college = request.POST.get("college")
        profile.year = request.POST.get("year")
        profile.bio = request.POST.get("bio")
        profile.career_goal = request.POST.get("career_goal")
        
        # Handle profile photo upload
        if request.FILES.get('profile_photo'):
            profile.profile_photo = request.FILES['profile_photo']
        
        profile.save()

        return redirect("profile")

    return render(request, "profile.html", {"profile": profile})

def calculate_study_streak(user):
    """Calculate current study streak in days"""
    activities = StudyActivity.objects.filter(user=user).order_by('-date')
    
    if not activities:
        return 0
    
    streak = 0
    current_date = timezone.now().date()
    
    for activity in activities:
        if activity.date == current_date - timedelta(days=streak):
            streak += 1
        else:
            break
    
    return streak

def calculate_mastery_percentage(user):
    """Calculate overall mastery percentage"""
    mastery_records = MasteryProgress.objects.filter(user=user)
    
    if not mastery_records:
        # Calculate based on completed tasks and study activities
        completed_tasks = Task.objects.filter(user=user, status='completed').count()
        total_tasks = Task.objects.filter(user=user).count()
        
        if total_tasks == 0:
            return 0
        
        base_mastery = (completed_tasks / total_tasks) * 100
        
        # Bonus for study activities
        study_bonus = min(StudyActivity.objects.filter(user=user).count() * 2, 20)
        
        return min(base_mastery + study_bonus, 100)
    
    # Average of all mastery levels
    return sum(record.mastery_level for record in mastery_records) / len(mastery_records)

@login_required
def tasks_view(request):
    """View for managing tasks"""
    if request.method == "POST":
        # Create new task
        title = request.POST.get("title")
        description = request.POST.get("description")
        priority = request.POST.get("priority")
        due_date_str = request.POST.get("due_date")
        
        task = Task.objects.create(
            user=request.user,
            title=title,
            description=description,
            priority=priority,
            due_date=datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M') if due_date_str else None
        )
        
        # Record study activity
        StudyActivity.objects.create(
            user=request.user,
            activity_type='task_created',
            duration_minutes=5
        )
        
        return redirect("tasks")
    
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "tasks.html", {"tasks": tasks})

@login_required
def complete_task(request, task_id):
    """Mark task as complete"""
    task = Task.objects.get(id=task_id, user=request.user)
    task.status = 'completed'
    task.save()
    
    # Record study activity
    StudyActivity.objects.create(
        user=request.user,
        activity_type='task_completed',
        duration_minutes=10
    )
    
    return redirect("tasks")

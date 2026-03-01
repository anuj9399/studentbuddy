from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stream = models.CharField(max_length=100, blank=True, null=True)
    college = models.CharField(max_length=150, blank=True, null=True)
    year = models.CharField(max_length=50, blank=True, null=True)
    
    # IMPORTANT
    career_goal = models.TextField(blank=True, null=True)
    
    # New fields for mastery tracking
    total_study_hours = models.FloatField(default=0.0)
    completed_tasks = models.IntegerField(default=0)
    mastery_percentage = models.FloatField(default=0.0)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    
    # New fields for study groups
    username = models.CharField(max_length=50, unique=True, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
            # Update user's completed tasks count
            profile, created = StudentProfile.objects.get_or_create(user=self.user)
            profile.completed_tasks += 1
            profile.save()
        super().save(*args, **kwargs)

class StudyActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50)  # 'study', 'notes', 'chat', etc.
    duration_minutes = models.IntegerField(default=0)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} on {self.date}"

class MasteryProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    topic = models.CharField(max_length=200)
    mastery_level = models.FloatField(default=0.0)  # 0-100
    last_studied = models.DateTimeField(auto_now=True)
    study_sessions = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.subject}: {self.topic}"

class CareerPath(models.Model):
    title = models.CharField(max_length=200)
    stream = models.CharField(max_length=100)  # Computer Science, Engineering, etc.
    description = models.TextField()
    average_salary = models.CharField(max_length=100)
    growth_rate = models.CharField(max_length=50)  # High, Medium, Low
    education_required = models.CharField(max_length=200)
    key_skills = models.TextField(help_text="Comma-separated skills")
    job_outlook = models.TextField()
    industries = models.TextField(help_text="Comma-separated industries")
    
    def __str__(self):
        return f"{self.title} ({self.stream})"

class CareerSkill(models.Model):
    career_path = models.ForeignKey(CareerPath, on_delete=models.CASCADE, related_name='required_skills')
    skill_name = models.CharField(max_length=100)
    importance = models.CharField(max_length=20, choices=[
        ('essential', 'Essential'),
        ('important', 'Important'),
        ('helpful', 'Helpful'),
    ])
    learn_time = models.CharField(max_length=100)  # e.g., "3-6 months"
    
    def __str__(self):
        return f"{self.skill_name} for {self.career_path.title}"

class CareerJourney(models.Model):
    career_path = models.ForeignKey(CareerPath, on_delete=models.CASCADE, related_name='journey_steps')
    step_number = models.IntegerField()
    step_title = models.CharField(max_length=200)
    step_description = models.TextField()
    duration = models.CharField(max_length=100)
    prerequisites = models.TextField(blank=True)
    outcomes = models.TextField()
    
    def __str__(self):
        return f"Step {self.step_number}: {self.step_title}"
    
    class Meta:
        ordering = ['step_number']

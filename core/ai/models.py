from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json

class StudyPlan(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    exam_date = models.DateField()
    total_study_hours_per_day = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    ai_schedule = models.JSONField(default=dict, help_text="AI generated schedule")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    @property
    def days_remaining(self):
        today = timezone.now().date()
        delta = self.exam_date - today
        return max(0, delta.days)
    
    @property
    def total_sessions(self):
        return StudySession.objects.filter(plan=self).count()
    
    @property
    def completed_sessions(self):
        return StudySession.objects.filter(plan=self, status='completed').count()
    
    @property
    def skipped_sessions(self):
        return StudySession.objects.filter(plan=self, status='skipped').count()
    
    @property
    def completion_percentage(self):
        total = self.total_sessions
        if total == 0:
            return 0
        completed = self.completed_sessions
        return round((completed / total) * 100, 1)

class PlanSubject(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    SUBJECT_COLORS = [
        '#7C3AED', '#3B82F6', '#10B981', '#F97316', '#EC4899', '#14B8A6'
    ]
    
    plan = models.ForeignKey(StudyPlan, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=100)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    topics_count = models.IntegerField(default=1)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    color = models.CharField(max_length=7, default='#7C3AED')
    
    def __str__(self):
        return f"{self.subject_name} - {self.plan.title}"
    
    def save(self, *args, **kwargs):
        if not self.color:
            # Assign color based on existing subjects count
            existing_count = PlanSubject.objects.filter(plan=self.plan).count()
            self.color = self.SUBJECT_COLORS[existing_count % len(self.SUBJECT_COLORS)]
        super().save(*args, **kwargs)

class StudySession(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
    ]
    
    SESSION_TYPES = [
        ('theory', 'Theory'),
        ('practice', 'Practice'),
        ('revision', 'Revision'),
    ]
    
    plan = models.ForeignKey(StudyPlan, on_delete=models.CASCADE)
    subject = models.ForeignKey(PlanSubject, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.IntegerField()
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='theory')
    topic_focus = models.CharField(max_length=200)
    tips = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.subject.subject_name} - {self.date}"

class StudyProgress(models.Model):
    plan = models.ForeignKey(StudyPlan, on_delete=models.CASCADE)
    subject = models.ForeignKey(PlanSubject, on_delete=models.CASCADE)
    completed_sessions = models.IntegerField(default=0)
    total_sessions = models.IntegerField(default=0)
    completion_percentage = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['plan', 'subject']
    
    def update_progress(self):
        total = StudySession.objects.filter(plan=self.plan, subject=self.subject).count()
        completed = StudySession.objects.filter(plan=self.plan, subject=self.subject, status='completed').count()
        
        self.total_sessions = total
        self.completed_sessions = completed
        self.completion_percentage = round((completed / total) * 100, 1) if total > 0 else 0
        self.save()

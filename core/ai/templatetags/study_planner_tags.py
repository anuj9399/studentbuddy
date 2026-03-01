from django import template
from ..models import StudySession

register = template.Library()

@register.filter
def get_progress(subject, plan):
    """Get completion percentage for a subject"""
    total = StudySession.objects.filter(plan=plan, subject=subject).count()
    if total == 0:
        return 0
    completed = StudySession.objects.filter(plan=plan, subject=subject, status='completed').count()
    return round((completed / total) * 100)

@register.filter
def get_completed_sessions(subject, plan):
    """Get completed sessions count for a subject"""
    return StudySession.objects.filter(plan=plan, subject=subject, status='completed').count()

@register.filter
def get_total_sessions(subject, plan):
    """Get total sessions count for a subject"""
    return StudySession.objects.filter(plan=plan, subject=subject).count()

@register.filter
def mul(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

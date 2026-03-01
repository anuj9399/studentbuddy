from django import template

register = template.Library()

@register.filter
def calculate_cgpa(semesters):
    """Calculate CGPA from queryset of semesters"""
    if not semesters:
        return 0.0
    
    total_credits = sum(sem.credits for sem in semesters)
    total_weighted_points = sum(sem.sgpa * sem.credits for sem in semesters)
    
    if total_credits == 0:
        return 0.0
    
    return total_weighted_points / total_credits

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class AcademicProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    university_name = models.CharField(max_length=200)
    university_short = models.CharField(max_length=50)
    pattern_year = models.CharField(max_length=4)  # 2019, 2022, 2023
    stream = models.CharField(max_length=50)  # Engineering, Science, Commerce
    branch = models.CharField(max_length=100)  # Computer Engineering
    grading_scale = models.DecimalField(max_digits=3, decimal_places=1, choices=[
        ('10.0', '10.0 Scale'),
        ('7.0', '7.0 Scale'),
        ('4.0', '4.0 Scale'),
    ])
    total_semesters = models.IntegerField(choices=[
        (6, '6 Semesters'),
        (8, '8 Semesters'),
        (10, '10 Semesters'),
    ])
    ai_analysis = models.TextField(blank=True, null=True)
    ai_improvement_advice = models.TextField(blank=True, null=True)
    
    # Individual benchmark fields for better data handling
    minimum_cgpa = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    good_cgpa = models.DecimalField(max_digits=3, decimal_places=1, default=7.0)
    excellent_cgpa = models.DecimalField(max_digits=3, decimal_places=1, default=9.0)
    placement_cutoff = models.DecimalField(max_digits=3, decimal_places=1, default=6.5)
    
    # University info fields
    university_info = models.TextField(blank=True, default='')
    pattern_info = models.TextField(blank=True, default='')
    benchmark_message = models.TextField(blank=True, default='')
    improvement_tips = models.TextField(blank=True, default='')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.university_short} - {self.branch}"

class Semester(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    semester_number = models.IntegerField()
    sgpa = models.DecimalField(max_digits=4, decimal_places=2)
    credits = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['semester_number']

    def __str__(self):
        return f"Semester {self.semester_number}"

    @property
    def weighted_points(self):
        """Calculate weighted points (SGPA * credits)"""
        return float(self.sgpa) * self.credits

    @property
    def status_badge(self):
        """Get status badge based on grading scale and SGPA"""
        try:
            profile = self.user.academicprofile
            grading_scale = float(profile.grading_scale)
            sgpa = float(self.sgpa)
            
            if grading_scale == 10.0:
                if sgpa >= 9.0:
                    return {"text": "Excellent", "color": "green"}
                elif sgpa >= 7.5:
                    return {"text": "Good", "color": "blue"}
                elif sgpa >= 6.0:
                    return {"text": "Average", "color": "yellow"}
                else:
                    return {"text": "Poor", "color": "red"}
                    
            elif grading_scale == 7.0:
                if sgpa >= 6.5:
                    return {"text": "Excellent", "color": "green"}
                elif sgpa >= 5.5:
                    return {"text": "Good", "color": "blue"}
                elif sgpa >= 4.5:
                    return {"text": "Average", "color": "yellow"}
                else:
                    return {"text": "Poor", "color": "red"}
                    
            elif grading_scale == 4.0:
                if sgpa >= 3.7:
                    return {"text": "Excellent", "color": "green"}
                elif sgpa >= 3.0:
                    return {"text": "Good", "color": "blue"}
                elif sgpa >= 2.0:
                    return {"text": "Average", "color": "yellow"}
                else:
                    return {"text": "Poor", "color": "red"}
            else:
                return {"text": "Average", "color": "yellow"}
                
        except:
            return {"text": "Average", "color": "yellow"}

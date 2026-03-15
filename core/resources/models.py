from django.db import models
from django.contrib.auth.models import User

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    university = models.CharField(max_length=200)
    stream = models.CharField(max_length=200)
    branch = models.CharField(max_length=200)
    semester = models.CharField(max_length=20)
    subject = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=100)
    searched_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-searched_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.subject} ({self.resource_type})"

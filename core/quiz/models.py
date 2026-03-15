from django.db import models
from django.contrib.auth.models import User

class Quiz(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    STATUS_CHOICES = [
        ('generating', 'Generating'),
        ('ready', 'Ready'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.CharField(max_length=300)
    subject = models.CharField(max_length=200, blank=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    total_questions = models.IntegerField(default=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generating')
    
    # University and academic details
    university = models.CharField(max_length=200, blank=True)
    stream = models.CharField(max_length=200, blank=True)
    branch = models.CharField(max_length=200, blank=True)
    year = models.CharField(max_length=100, blank=True)
    pattern = models.CharField(max_length=100, blank=True)
    chapter = models.CharField(max_length=300, blank=True)

    # Attempt tracking
    current_question = models.IntegerField(default=0)
    score = models.IntegerField(default=0)
    time_taken = models.IntegerField(default=0)  # in seconds

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def get_percentage(self):
        if self.total_questions == 0:
            return 0
        return round((self.score / self.total_questions) * 100)


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_number = models.IntegerField()
    question_text = models.TextField()

    # Options
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)

    correct_option = models.CharField(max_length=1)  # A, B, C, or D
    explanation = models.TextField(blank=True)

    # Student answer
    selected_option = models.CharField(max_length=1, blank=True)
    is_correct = models.BooleanField(null=True)
    time_spent = models.IntegerField(default=0)  # seconds on this question

    class Meta:
        ordering = ['question_number']

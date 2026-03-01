from django.db import models
from django.contrib.auth.models import User

class ExamSubject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject_name = models.CharField(max_length=200)
    total_papers_uploaded = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.subject_name} - {self.user.username}"
    
    @property
    def latest_analysis(self):
        try:
            return self.examanalysis_set.latest('analyzed_at')
        except ExamAnalysis.DoesNotExist:
            return None

class QuestionPaper(models.Model):
    subject = models.ForeignKey(ExamSubject, on_delete=models.CASCADE)
    file = models.FileField(upload_to='exam_papers/')
    year = models.IntegerField()
    extracted_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.subject.subject_name} - {self.year}"

class ExamAnalysis(models.Model):
    subject = models.ForeignKey(ExamSubject, on_delete=models.CASCADE)
    most_repeated_topics = models.JSONField(default=list, help_text="List of topics with frequency data")
    high_probability_topics = models.JSONField(default=list, help_text="Topics likely to appear in next exam")
    chapter_weightage = models.JSONField(default=list, help_text="Chapter-wise marks distribution")
    question_pattern = models.JSONField(default=dict, help_text="Question pattern analysis")
    predicted_questions = models.JSONField(default=list, help_text="AI predicted questions")
    study_priority_list = models.JSONField(default=list, help_text="Prioritized study topics")
    quick_insights = models.JSONField(default=list, help_text="Quick insights from analysis")
    raw_ai_response = models.TextField(blank=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-analyzed_at']
    
    def __str__(self):
        return f"Analysis for {self.subject.subject_name}"
    
    @property
    def total_topics_found(self):
        return len(self.most_repeated_topics) if self.most_repeated_topics else 0
    
    @property
    def high_priority_topics_count(self):
        if not self.most_repeated_topics:
            return 0
        return len([t for t in self.most_repeated_topics if t.get('importance') == 'high'])
    
    @property
    def predicted_questions_count(self):
        return len(self.predicted_questions) if self.predicted_questions else 0

from django.urls import path
from . import views

app_name = 'exam_analyzer'

urlpatterns = [
    path('', views.analyzer_home, name='analyzer_home'),
    path('subject/create/', views.create_subject, name='create_subject'),
    path('subject/<int:subject_id>/upload/', views.upload_papers, name='upload_papers'),
    path('subject/<int:subject_id>/analyze/', views.run_analysis, name='run_analysis'),
    path('subject/<int:subject_id>/analysis/', views.analysis_results, name='analysis_results'),
    path('paper/<int:paper_id>/delete/', views.delete_paper, name='delete_paper'),
    path('subject/<int:subject_id>/delete/', views.delete_subject, name='delete_subject'),
]

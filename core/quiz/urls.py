from django.urls import path
from . import views

app_name = 'quiz'

urlpatterns = [
    path('', views.quiz_home, name='home'),
    path('create/', views.create_quiz, name='create'),
    path('<int:quiz_id>/attempt/', views.quiz_attempt, name='attempt'),
    path('<int:quiz_id>/submit/', views.submit_answer, name='submit'),
    path('<int:quiz_id>/results/', views.quiz_results, name='results'),
]

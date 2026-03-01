from django.urls import path
from . import views

app_name = 'grade_tracker'

urlpatterns = [
    path('setup/', views.grade_setup, name='grade_setup'),
    path('', views.grade_dashboard, name='grade_dashboard'),
    path('add/', views.add_semester, name='add_semester'),
    path('delete/<int:semester_id>/', views.delete_semester, name='delete_semester'),
    path('print/', views.print_report, name='print_report'),
    path('reanalyse/', views.reanalyse_university, name='reanalyse_university'),
]

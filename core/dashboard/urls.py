from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("career/", views.career, name="career"),
    path("planner/", views.study_planner, name="planner"),
]

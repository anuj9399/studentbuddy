from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat, name='chat'),
    path("notes/", views.smart_notes, name="smart_notes"),
    path("planner/", views.planner, name='planner'),
    path("planner/create/", views.create_plan, name='create_plan'),
    path("planner/<int:plan_id>/", views.plan_detail, name='plan_detail'),
    path("planner/session/<int:session_id>/complete/", views.mark_session_complete, name='mark_session_complete'),
    path("planner/session/<int:session_id>/skip/", views.skip_session, name='skip_session'),
    path("planner/<int:plan_id>/delete/", views.delete_plan, name='delete_plan'),
    path("planner/test/", views.planner_test, name='planner_test'),
    path("planner/simple/", views.planner_simple, name='planner_simple'),
    path("career/", views.career, name='career'),
    path("career/test/", views.career_test, name='career_test'),
    path("career/simple/", views.career_simple_test, name='career_simple_test'),
]

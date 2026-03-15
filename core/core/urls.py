from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from .views import profile, dashboard, tasks_view, complete_task, about_us


urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('chat/', include('ai.urls')),
    path('', include('accounts.urls')),
    path("profile/", profile, name="profile"),
    path("tasks/", tasks_view, name="tasks"),
    path("tasks/complete/<int:task_id>/", complete_task, name="complete_task"),
    path('study-groups/', include('groups.urls')),
    path('exam-analyzer/', include('exam_analyzer.urls')),
    path('grades/', include('grade_tracker.urls')),
    path('resources/', include('resources.urls')),
    path('quiz/', include('quiz.urls')),
    path('about/', about_us, name='about'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += [
        path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

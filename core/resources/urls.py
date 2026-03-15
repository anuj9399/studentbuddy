from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    path('', views.resource_home, name='home'),
    path('search/', views.search_resources, name='search'),
]

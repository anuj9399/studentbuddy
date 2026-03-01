from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    path('', views.group_list, name='group_list'),
    path('create/', views.group_create, name='group_create'),
    path('<int:group_id>/', views.group_detail, name='group_detail'),
    path('invite/', views.group_invite, name='group_invite'),
    path('send-invite/', views.send_invite, name='send_invite'),
    path('send-message/<int:group_id>/', views.send_message, name='send_message'),
    path('get-messages/<int:group_id>/', views.get_messages, name='get_messages'),
    path('accept-invite/<int:invite_id>/', views.accept_invite, name='accept_invite'),
    path('reject-invite/<int:invite_id>/', views.reject_invite, name='reject_invite'),
    path('save-note/<int:group_id>/', views.save_note, name='save_note'),
    path('upload-file/<int:group_id>/', views.upload_file, name='upload_file'),
    path('remove-member/<int:group_id>/<int:user_id>/', views.remove_member, name='remove_member'),
    path('delete-group/<int:group_id>/', views.delete_group, name='delete_group'),
    path('delete-message/<int:message_id>/', views.delete_message, name='delete_message'),
]

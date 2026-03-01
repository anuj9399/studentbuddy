from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import models
from .models import StudyGroup, GroupInvite, GroupMessage, SharedNote, SharedFile
from accounts.models import StudentProfile, StudyActivity

@login_required
def group_list(request):
    """List of groups the student is in + pending invites"""
    user_groups = StudyGroup.objects.filter(members=request.user)
    pending_invites = GroupInvite.objects.filter(invited_user=request.user, status='pending')
    
    context = {
        'user_groups': user_groups,
        'pending_invites': pending_invites,
    }
    return render(request, 'groups/group_list.html', context)

@login_required
def group_create(request):
    """Create a new group"""
    if request.method == 'POST':
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        
        if name and subject:
            group = StudyGroup.objects.create(
                name=name,
                subject=subject,
                description=description,
                created_by=request.user
            )
            group.members.add(request.user)
            
            # Create shared note for the group
            SharedNote.objects.create(group=group)
            
            # Record activity
            StudyActivity.objects.create(
                user=request.user,
                activity_type='study_group',
                duration_minutes=10
            )
            
            messages.success(request, f'Group "{name}" created successfully!')
            return redirect('groups:group_detail', group.id)
    
    return render(request, 'groups/group_create.html')

@login_required
def group_detail(request, group_id):
    """Group detail page with tabs"""
    group = get_object_or_404(StudyGroup, id=group_id)
    
    # Check if user is member
    if request.user not in group.members.all():
        messages.error(request, 'You are not a member of this group.')
        return redirect('groups:group_list')
    
    # Get shared note
    shared_note, created = SharedNote.objects.get_or_create(group=group)
    
    # Get recent messages
    messages = GroupMessage.objects.filter(group=group).order_by('-timestamp')[:50]
    
    # Get files
    files = SharedFile.objects.filter(group=group).order_by('-uploaded_at')
    
    context = {
        'group': group,
        'shared_note': shared_note,
        'messages': messages,
        'files': files,
        'is_admin': group.created_by == request.user,
    }
    return render(request, 'groups/group_detail.html', context)

@login_required
def group_invite(request):
    """Search and invite users to group"""
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        search_query = request.POST.get('search', '').strip()
        
        print(f"DEBUG: group_invite called with group_id={group_id}, search_query={search_query}")
        
        group = get_object_or_404(StudyGroup, id=group_id)
        
        # Check if user is admin
        if group.created_by != request.user:
            print(f"DEBUG: User {request.user.username} is not admin of group {group.name}")
            return JsonResponse({'error': 'Only group admin can invite members'}, status=403)
        
        # Search users by username or email
        users = User.objects.filter(
            models.Q(username__icontains=search_query) | 
            models.Q(email__icontains=search_query)
        ).exclude(id=request.user.id)
        
        print(f"DEBUG: Found {users.count()} users matching search")
        
        # Filter out existing members and already invited users
        existing_members = group.members.all()
        invited_users = GroupInvite.objects.filter(group=group, status='pending').values_list('invited_user', flat=True)
        
        users = users.exclude(id__in=existing_members).exclude(id__in=invited_users)
        
        print(f"DEBUG: After filtering, {users.count()} users available for invitation")
        
        user_data = []
        for user in users:
            try:
                profile = user.studentprofile
                user_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'branch': profile.branch or '',
                    'year': profile.year or '',
                })
            except StudentProfile.DoesNotExist:
                user_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'branch': '',
                    'year': '',
                })
        
        print(f"DEBUG: Returning user_data: {user_data}")
        return JsonResponse({'users': user_data})
    
    print("DEBUG: Invalid request method")
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@require_POST
def send_invite(request):
    """Send group invite"""
    group_id = request.POST.get('group_id')
    user_id = request.POST.get('user_id')
    
    print(f"DEBUG: send_invite called with group_id={group_id}, user_id={user_id}")
    
    group = get_object_or_404(StudyGroup, id=group_id)
    invited_user = get_object_or_404(User, id=user_id)
    
    print(f"DEBUG: Group: {group.name}, Invited user: {invited_user.username}, Invited by: {request.user.username}")
    
    # Check if user is admin
    if group.created_by != request.user:
        print(f"DEBUG: User {request.user.username} is not admin of group {group.name}")
        return JsonResponse({'error': 'Only group admin can invite members'}, status=403)
    
    # Create invite
    invite, created = GroupInvite.objects.get_or_create(
        group=group,
        invited_by=request.user,
        invited_user=invited_user,
        defaults={'status': 'pending'}
    )
    
    print(f"DEBUG: Invite created: {created}, Invite status: {invite.status}")
    
    if created:
        return JsonResponse({'success': 'Invite sent successfully'})
    else:
        return JsonResponse({'error': 'Invite already sent'}, status=400)

@login_required
@require_POST
def accept_invite(request, invite_id):
    """Accept group invite"""
    invite = get_object_or_404(GroupInvite, id=invite_id, invited_user=request.user)
    
    if invite.status == 'pending':
        invite.status = 'accepted'
        invite.group.members.add(request.user)
        invite.save()
        
        messages.success(request, f'You joined "{invite.group.name}"!')
    
    return redirect('groups:group_list')

@login_required
@require_POST
def reject_invite(request, invite_id):
    """Reject group invite"""
    invite = get_object_or_404(GroupInvite, id=invite_id, invited_user=request.user)
    
    if invite.status == 'pending':
        invite.status = 'rejected'
        invite.save()
    
    return redirect('groups:group_list')

@login_required
@require_POST
def save_note(request, group_id):
    """Save shared note"""
    group = get_object_or_404(StudyGroup, id=group_id)
    
    # Check if user is member
    if request.user not in group.members.all():
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    content = request.POST.get('content', '')
    
    shared_note, created = SharedNote.objects.get_or_create(group=group)
    shared_note.content = content
    shared_note.last_edited_by = request.user
    shared_note.save()
    
    return JsonResponse({
        'success': True,
        'last_edited_by': request.user.username,
        'updated_at': shared_note.updated_at.strftime('%Y-%m-%d %H:%M:%S')
    })

@login_required
def upload_file(request, group_id):
    """Upload file to group"""
    group = get_object_or_404(StudyGroup, id=group_id)
    
    # Check if user is member
    if request.user not in group.members.all():
        messages.error(request, 'Access denied')
        return redirect('groups:group_detail', group_id)
    
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        
        shared_file = SharedFile.objects.create(
            group=group,
            uploaded_by=request.user,
            file=uploaded_file,
            filename=uploaded_file.name
        )
        
        messages.success(request, f'File "{uploaded_file.name}" uploaded successfully!')
    
    return redirect('groups:group_detail', group_id)

@login_required
@require_POST
def remove_member(request, group_id, user_id):
    """Remove member from group (admin only)"""
    group = get_object_or_404(StudyGroup, id=group_id)
    member_to_remove = get_object_or_404(User, id=user_id)
    
    # Check if user is admin
    if group.created_by != request.user:
        return JsonResponse({'error': 'Only group admin can remove members'}, status=403)
    
    # Don't allow removing admin
    if member_to_remove == group.created_by:
        return JsonResponse({'error': 'Cannot remove group admin'}, status=400)
    
    group.members.remove(member_to_remove)
    
    return JsonResponse({'success': 'Member removed successfully'})

@login_required
@require_POST
def delete_group(request, group_id):
    """Delete group (admin only)"""
    group = get_object_or_404(StudyGroup, id=group_id)
    
    # Check if user is admin
    if group.created_by != request.user:
        return JsonResponse({'error': 'Only group admin can delete group'}, status=403)
    
    group.delete()
    
    return JsonResponse({'success': 'Group deleted successfully'})

@login_required
def get_messages(request, group_id):
    """Get recent chat messages for refresh"""
    group = get_object_or_404(StudyGroup, id=group_id)
    
    # Check if user is member
    if request.user not in group.members.all():
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Get recent messages (last 50)
    messages = GroupMessage.objects.filter(group=group).order_by('-timestamp')[:50]
    
    message_data = []
    for message in reversed(messages):  # Reverse to show oldest first
        message_data.append({
            'id': message.id,
            'message': message.message,
            'sender': message.sender.username,
            'timestamp': message.timestamp.isoformat(),
        })
    
    return JsonResponse({'messages': message_data})

@login_required
@require_POST
def send_message(request, group_id):
    """Send chat message via HTTP (WebSocket fallback)"""
    group = get_object_or_404(StudyGroup, id=group_id)
    
    # Check if user is member
    if request.user not in group.members.all():
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    message = request.POST.get('message', '').strip()
    
    if message:
        # Create message
        group_message = GroupMessage.objects.create(
            group=group,
            sender=request.user,
            message=message
        )
        
        return JsonResponse({
            'success': True,
            'message_id': group_message.id
        })
    
    return JsonResponse({'error': 'Message cannot be empty'}, status=400)

@login_required
@require_POST
def delete_message(request, message_id):
    """Delete chat message (admin or message sender only)"""
    message = get_object_or_404(GroupMessage, id=message_id)
    group = message.group
    
    # Check if user is admin or message sender
    if group.created_by != request.user and message.sender != request.user:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Delete message
    message.delete()
    
    return JsonResponse({'success': True})

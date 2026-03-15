import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import StudyGroup, GroupMessage

class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f"🔌 WebSocket connection attempt for group_id: {self.scope['url_route']['kwargs']['group_id']}")
        print(f"👤 User: {self.scope.get('user', 'Anonymous')} (authenticated: {self.scope.get('user', {}).is_authenticated if self.scope.get('user') else False})")
        
        # Get user from scope (handle both authenticated and anonymous)
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            print("❌ User not authenticated, closing connection")
            await self.close(code=4001)  # Custom code for authentication failure
            return
            
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        self.group_obj = await self.get_group()
        
        # Check if group exists
        if not self.group_obj:
            print(f"❌ Group {self.group_id} not found, closing connection")
            await self.close(code=4004)  # Custom code for not found
            return
            
        # Check if user is a member of the group
        is_member = await self.is_user_member()
        if not is_member:
            print(f"❌ User {user.username} not member of group {self.group_id}, closing connection")
            await self.close(code=4003)  # Custom code for forbidden
            return
            
        self.group_name = f'group_{self.group_id}'
        print(f"✅ User {user.username} connected to group {self.group_id}")

        # Join room group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()
        print(f"🎉 WebSocket connection accepted for group {self.group_id}")

    async def disconnect(self, close_code):
        print(f"🔌 WebSocket disconnected for group {self.group_id}, code: {close_code}")
        # Leave room group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'chat_message')
        
        if message_type == 'chat_message':
            message = text_data_json['message']
            sender = self.scope['user']
            
            # Save message to database
            saved_message = await self.save_message(sender, message)
            
            # Send message to room group with message ID
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender.username,
                    'timestamp': timezone.now().strftime('%H:%M'),
                    'message_id': saved_message.id if saved_message else None
                }
            )
        elif message_type == 'delete_message':
            message_id = text_data_json.get('message_id')
            sender = self.scope['user']
            
            # Check if user can delete this message
            can_delete = await self.can_delete_message(sender, message_id)
            
            if can_delete:
                # Delete message from database
                success = await self.delete_message(sender, message_id)
                
                if success:
                    # Broadcast deletion to room group
                    await self.channel_layer.group_send(
                        self.group_name,
                        {
                            'type': 'delete_message',
                            'message_id': message_id,
                            'deleted_by': sender.username
                        }
                    )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        timestamp = event['timestamp']
        message_id = event.get('message_id')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'sender': sender,
            'timestamp': timestamp,
            'message_id': message_id
        }))

    # Handle message deletion
    async def delete_message(self, event):
        message_id = event['message_id']
        deleted_by = event['deleted_by']

        # Send deletion event to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'delete_message',
            'message_id': message_id,
            'deleted_by': deleted_by
        }))

    @database_sync_to_async
    def get_group(self):
        try:
            return StudyGroup.objects.get(id=self.group_id)
        except StudyGroup.DoesNotExist:
            return None

    @database_sync_to_async
    def is_user_member(self):
        user = self.scope["user"]
        return self.group_obj.members.filter(id=user.id).exists()

    @database_sync_to_async
    def save_message(self, sender, message):
        if self.group_obj:
            return GroupMessage.objects.create(
                group=self.group_obj,
                sender=sender,
                message=message
            )
        return None

    @database_sync_to_async
    def can_delete_message(self, sender, message_id):
        try:
            message = GroupMessage.objects.get(id=message_id)
            group = message.group
            
            # Check if user is admin or message sender
            return group.created_by == sender or message.sender == sender
        except GroupMessage.DoesNotExist:
            return False

    @database_sync_to_async
    def delete_message(self, sender, message_id):
        try:
            message = GroupMessage.objects.get(id=message_id)
            group = message.group
            
            # Check if user is admin or message sender
            if group.created_by == sender or message.sender == sender:
                message.delete()
                return True
        except GroupMessage.DoesNotExist:
            pass
        return False

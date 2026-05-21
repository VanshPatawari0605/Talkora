import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message, User


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Check if user is member of this room
        is_member = await self.check_membership(self.room_id, self.scope['user'])
        if not is_member:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Mark user online
        await self.set_online_status(self.scope['user'], True)

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        # Mark user offline
        await self.set_online_status(self.scope['user'], False)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        user = self.scope['user']

        # Save message to DB
        saved = await self.save_message(user, self.room_id, message)

        # Broadcast to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': user.username,
                'sender_id': user.id,
                'timestamp': str(saved.timestamp),
                'pfp': saved.sender.profile_picture.url if saved.sender.profile_picture else None,
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp'],
            'pfp': event['pfp'],
        }))

    @database_sync_to_async
    def check_membership(self, room_id, user):
        if not user.is_authenticated:
            return False
        return user.rooms.filter(id=room_id).exists()

    @database_sync_to_async
    def save_message(self, user, room_id, content):
        room = Room.objects.get(id=room_id)
        message = Message.objects.create(room=room, sender=user, content=content)
        # Refresh to get related sender data
        message.sender = User.objects.get(id=user.id)
        return message

    @database_sync_to_async
    def set_online_status(self, user, status):
        if user.is_authenticated:
            User.objects.filter(id=user.id).update(is_online=status)
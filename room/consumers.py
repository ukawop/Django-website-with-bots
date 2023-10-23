import json
import base64
from django.core.files.base import ContentFile

from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.files.storage import default_storage

from .models import Room, CloneRoom, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        image = data.get('image', None)
        username = data['username']
        room = data['room']
        if image:
            format, imgstr = image.split(';base64,')
            ext = format.split('/')[-1]
            image = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            print(image)

        await self.save_message(username, room, message, image)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'image': data.get('image', None),
                'username': username
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        image = event['image']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'image': image
        }))


    @sync_to_async
    def save_message(self, username, room, message, image):
        user = User.objects.get(username=username)
        room = Room.objects.get(slug=room)
        if image:
            image = default_storage.save(image.name, image)
        if room.is_group:
            Message.objects.create(user=user, room=room, content=message, image=image)
        else:
            clone_room = CloneRoom.objects.get(room=room, user=user)
            Message.objects.create(user=user, room=room, clone_room=clone_room, content=message, image=image)

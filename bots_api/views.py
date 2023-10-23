import base64
import mimetypes
import os
import secrets

from django.core.files.base import ContentFile
from django.http import FileResponse, HttpResponseNotFound
from django.views import View
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, generics

from django.contrib.auth.models import User
from room.models import Room, Message, CloneRoom
from .serializers import (MessageInfoSerializer,
                          MessageCreateTextSerializer,
                          MessageCreateImageSerializer,
                          MessageUpdateSerializer,
                          MessageDeleteSerializer,
                          MessageBotUpdateSerializer)

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.core.exceptions import ObjectDoesNotExist
from functools import wraps


def handle_does_not_exist(view_class):
    """Декоратор для ловли ошибок"""
    def wrap_view_method(view_method):
        @wraps(view_method)
        def wrapper(self, *args, **kwargs):
            try:
                return view_method(self, *args, **kwargs)
            except ObjectDoesNotExist:
                return HttpResponseNotFound()

        return wrapper

    for method_name in [name for name in dir(view_class) if name.startswith(('get', 'post', 'patch', 'delete'))]:
        view_method = getattr(view_class, method_name)
        setattr(view_class, method_name, wrap_view_method(view_method))

    return view_class


@handle_does_not_exist
class MessageGetUpdatesView(APIView):
    """Представление для отображения обновлений"""
    def get(self, request, bot_token):
        message = Message.objects.filter(room__bot_token=bot_token, is_bot=False).order_by('-date_added')[:25][::-1]

        serializer = MessageInfoSerializer(message, many=True)

        return Response(serializer.data)


@handle_does_not_exist
class MessageIDView(APIView):
    """Представление для отображения, изменения и удаления сообщений по id"""
    def get(self, request, bot_token, id):
        id_message = id
        message = Message.objects.filter(room__bot_token=bot_token, id=id_message, is_bot=False).latest('date_added')

        serializer = MessageInfoSerializer(message)

        return Response(serializer.data)

    @swagger_auto_schema(request_body=MessageUpdateSerializer)
    def patch(self, request, bot_token, id):
        new_content = request.data.get('content', '')
        id_message = id

        latest_message = Message.objects.get(room__bot_token=bot_token, id=id_message)
        latest_message.content = new_content
        latest_message.save()

        return Response(status=200)

    def delete(self, request, bot_token, id):
        id_message = id
        Message.objects.filter(room__bot_token=bot_token, id=id_message).delete()

        return Response(status=204)


@handle_does_not_exist
class MessageBotLastView(APIView):
    """Представление для отображения, изменения и удаления последнего сообщения присланного с помощью API"""
    def get(self, request, bot_token):
        message = Message.objects.filter(room__bot_token=bot_token, is_bot=True).latest('date_added')

        serializer = MessageInfoSerializer(message)

        return Response(serializer.data)

    @swagger_auto_schema(request_body=MessageBotUpdateSerializer)
    def patch(self, request, bot_token):
        new_content = request.data.get('content', '')

        latest_message = Message.objects.filter(room__bot_token=bot_token, is_bot=True).latest('date_added')
        latest_message.content = new_content
        latest_message.save()

        return Response(status=200)

    def delete(self, request, bot_token):
        Message.objects.filter(room__bot_token=bot_token, is_bot=True).latest('date_added').delete()

        return Response(status=204)


@handle_does_not_exist
class MessageEveryLastInfoView(APIView):
    """Представление для отображения последнего сообщения каждого пользователя в группе"""
    def get(self, request, bot_token):
        raw_query = """
            SELECT m.* 
            FROM messages m
            INNER JOIN room r ON m.room_id = r.id
            WHERE m.date_added IN (
                SELECT MAX(date_added) 
                FROM messages 
                WHERE room_id IN (
                    SELECT id 
                    FROM room 
                    WHERE bot_token = %s
                ) AND NOT messages.is_bot
                GROUP BY user_id
            )
        """
        message = Message.objects.raw(raw_query, [bot_token])
        serializer = MessageInfoSerializer(message, many=True)
        return Response(serializer.data)


class MessageSendTextView(APIView):
    """Представление для отправки сообщения"""

    @swagger_auto_schema(request_body=MessageCreateTextSerializer)
    def post(self, request, bot_token):
        message = request.data.get('content', '')
        room_name = request.data.get('room', '')
        id_clone_room = request.data.get('clone_room', None)
        room_slug = Room.objects.get(bot_token=bot_token).slug

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{room_slug}',
            {
                'type': 'chat_message',
                'message': message,
                'image': '',
                'username': 'BOT'
            }
        )
        user, created = User.objects.get_or_create(username='BOT')
        if created:
            user.set_password(secrets.token_urlsafe(30))
            user.save()
        room = Room.objects.get(name=room_name)
        clone_room = CloneRoom.objects.filter(id=id_clone_room).first()
        new_message = Message.objects.create(user=user, room=room, clone_room=clone_room, content=message, is_bot=True)
        new_message.save()
        return Response(status=201)


class MessageSendImageView(APIView):
    """Представление для отправки изображений"""

    @swagger_auto_schema(request_body=MessageCreateImageSerializer)
    def post(self, request, bot_token):
        message = request.data.get('caption', '')
        id_clone_room = request.data.get('clone_room', None)
        image = request.data.get('image', '')
        room = Room.objects.get(bot_token=bot_token)
        js_image = 'data:image/jpeg;base64,' + image


        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'chat_{room.slug}',
            {
                'type': 'chat_message',
                'message': message,
                'image': js_image,
                'username': 'BOT'
            }
        )

        if image:
            image = ContentFile(base64.b64decode(image), name='temp.' + 'jpeg')

        user, created = User.objects.get_or_create(username='BOT')
        if created:
            user.set_password(secrets.token_urlsafe(30))
            user.save()


        clone_room = CloneRoom.objects.filter(id=id_clone_room).first()
        new_message = Message.objects.create(user=user, room=room, clone_room=clone_room, content=message, image=image, is_bot=True)
        new_message.save()

        return Response(status=201)


@handle_does_not_exist
class TakeImageView(View):
    """Представление для отображения изображения по заданному пути"""
    def get(self, request, bot_token, path):
        _message = Message.objects.filter(room__bot_token=bot_token, image=f'media/{path}')
        full_path = os.path.join(settings.MEDIA_ROOT, path)

        if not os.path.exists(full_path):
            return HttpResponseNotFound()

        response = FileResponse(open(full_path, 'rb'))
        response['Content-Disposition'] = 'inline; filename=' + os.path.basename(full_path)

        mimetype, encoding = mimetypes.guess_type(full_path)
        if mimetype is None:
            mimetype = 'application/octet-stream'
        response['Content-Type'] = mimetype

        return response

'''
    {
        "room": "just a chat",
        "content": "HELLO",
        "clone_room": null
    }
'''

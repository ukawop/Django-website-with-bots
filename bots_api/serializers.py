from rest_framework import serializers

from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from django.db.models.fields import TextField
from room.models import Room, CloneRoom, Message


class MessageInfoSerializer(serializers.ModelSerializer):
    room = serializers.SlugRelatedField(slug_field='name', read_only=True)
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Message
        fields = '__all__'


class MessageCreateTextSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=255)
    room = serializers.CharField(max_length=50)
    clone_room = serializers.IntegerField(default=None)
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Message
        exclude = ('is_bot',)


class MessageCreateImageSerializer(serializers.ModelSerializer):
    image = serializers.CharField()
    caption = serializers.CharField(max_length=255, default=None)
    room = serializers.CharField(max_length=50)
    clone_room = serializers.IntegerField(default=None)
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    content = serializers.CharField(read_only=True)

    class Meta:
        model = Message
        exclude = ('is_bot',)


class MessageUpdateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=255)
    room = serializers.SlugRelatedField(slug_field='name', read_only=True)
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Message
        fields = ['content', 'room', 'user']


class MessageDeleteSerializer(serializers.ModelSerializer):
    room = serializers.SlugRelatedField(slug_field='name', read_only=True)
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Message
        fields = '__all__'


class MessageBotUpdateSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=255)
    room = serializers.SlugRelatedField(slug_field='name', read_only=True)
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Message
        fields = ['content', 'room', 'user']
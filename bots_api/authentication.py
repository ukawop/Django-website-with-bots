from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from room.models import Room


def is_token_correct(func):
    def _wrapper(obj, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token:
            try:
                room = Room.objects.get(bot_token=token)
                return (room, token)

            except Room.DoesNotExist:
                raise AuthenticationFailed('Invalid API key')

        return None

    return _wrapper


class MyCustomAuthentication(BaseAuthentication):
    @is_token_correct
    def authenticate(self, request):
        pass

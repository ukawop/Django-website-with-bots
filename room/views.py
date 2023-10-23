from django.contrib.auth.decorators import login_required
from django.shortcuts import render


from .models import Room, CloneRoom, Message

@login_required
def rooms(request):
    rooms = Room.objects.all()

    return render(request, 'room/rooms.html', {'rooms': rooms})

@login_required
def room(request, slug):
    room = Room.objects.get(slug=slug)
    if room.is_group:
        messages = Message.objects.filter(room=room).order_by('-date_added')[0:25][::-1]
        return render(request, 'room/room.html', {'room': room, 'messages': messages})
    else:
        clone_room, created = CloneRoom.objects.get_or_create(room=room, user=request.user)
        messages = Message.objects.filter(clone_room=clone_room).order_by('-date_added')[0:25][::-1]
        return render(request, 'room/room.html', {'room': room, 'messages': messages})











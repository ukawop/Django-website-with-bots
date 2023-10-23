from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import secrets

from django.contrib.auth.models import User
from room.models import Room

from .forms import SignUpForm, AddBotForm


def frontpage(request):
    return render(request, 'core/frontpage.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            return redirect('frontpage')
    else:
        form = SignUpForm()

    return render(request, 'core/signup.html', {'form': form})



@login_required
def create_bot(request):
    if request.method == 'POST':
        form = AddBotForm(request.POST)
        if form.is_valid():
            user = request.user
            print(form.data)
            name = form.data['name']
            if 'is_group' in form.data:
                is_group = True
            else:
                is_group = False

            def generate_token():
                return secrets.token_urlsafe(30)

            new_room = Room.objects.create(user=user, name=name, is_group=is_group, bot_token=generate_token())
            new_room.save()


            return redirect('addbot')
    else:
        form = AddBotForm()

    return render(request, 'core/addbot.html', {'form': form, 'rooms': Room.objects.filter(user=request.user)})
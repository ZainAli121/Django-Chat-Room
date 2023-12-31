from django.shortcuts import render, redirect
from django.db.models import Q
from .models import *
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
# Create your views here.

def home(request):
    query = request.GET.get('query') if request.GET.get('query') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=query) |
        Q(name__icontains = query) |
        Q(desc__icontains = query)
                                )

    topics = Topic.objects.all()[0:7]
    rooms_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=query))
    context = {'rooms': rooms, 'topics' : topics, 'rooms_count': rooms_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id = pk)
    room_messages = room.message_set.all()
    members = room.members.all()
    if request.method == 'POST':
        message = Message.objects.create(
           user = request.user,
           room = room,
           body = request.POST.get('body')
        )
        room.members.add(request.user)
        return redirect('room', pk=room.id)
    
    context = {'room': room, 'room_messages': room_messages, 'members':members}
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
            topic_name = request.POST.get('topic')
            topic, created = Topic.objects.get_or_create(name=topic_name)

            Room.objects.create(
                host = request.user,
                topic = topic,
                name = request.POST.get('name'),
                desc = request.POST.get('desc'),
            )
        # form = RoomForm(request.POST)
        # if form.is_valid:
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     room.save()
            return redirect('home')
    context = {'form' : form, 'topics':topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not host of this room')
    
    form = RoomForm(instance=room)
    if request.method == 'POST':
            topic_name = request.POST.get('topic')
            topic, created = Topic.objects.get_or_create(name=topic_name)
            room.name = request.POST.get('name')
            room.topic = topic
            room.desc = request.POST.get('desc')
            room.save()
            
            return redirect('home')
    context = {'form':form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not host of this room')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


def loginUser(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')  
        user = User.objects.get(username=username)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request,'Incorrect username or password')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    form = MyUserCreationForm()
    
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        
        else:
            messages.error(request, 'Error occured during registration')

    context = {'form': form}
    return render(request, 'base/login_register.html', context)

@login_required(login_url='login')
def deleteMessage(request, pk):
    room = Room.objects.get(id = pk)
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You cannot delete this message!')
    
    if request.method == 'POST':
        message.delete()
        return redirect('room', pk=room.id)
    return render(request, 'base/delete.html', {'obj': message})

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/userProfile.html', context)


@login_required(login_url='login')
def updateProfile(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid:
            form.save()
            return redirect('user-profile', pk=user.id)

    
    context = {'form': form}
    return render (request, 'base/edit-user.html', context)

def roomTopics(request):
    query = request.GET.get('query') if request.GET.get('query') != None else ''
    topics = Topic.objects.filter(name__icontains=query)
    context = {'topics': topics}
    return render(request, 'base/topics.html', context)

def activity(request):
    room_messages = Message.objects.all()
    context = {'room_messages': room_messages}
    return render(request, 'base/activity.html', context)
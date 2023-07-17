from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from .models import Room, Topic, Message, UserProfile
from .forms import RoomForm
from django.db.models import Count
import re

'''rooms=[
    {'id':1, 'name':'Bud'},
    {'id':2, 'name':'study'},
    {'id':3, 'name':'foda'},
]'''



def loginPage(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Username or password incorrect')
        except:
            messages.error(request, 'User doesn\'t exist')

    
    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerUser(request):
    page = 'register'
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        print(form)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            userProfile = UserProfile(user=user, name=user.username)
            userProfile.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'As error has occurred. Please try again')
    context = {'page' : page, 'form' : form}

    return render(request, 'base/login_register.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    roomss = Room.objects.filter(Q(topic__name__icontains=q) |
                                 Q(name__icontains=q) |
                                 Q(description__icontains=q) |
                                 Q(host__username__icontains=q))
    
    room_count = roomss.count()

    topics = Topic.objects.alias(nroom=Count('room')).order_by('-nroom')[0:5]

    room_messages = Message.objects.filter(Q(room__topic__name__icontains = q))
    
    context = {'rooms': roomss, 'topics':topics, 'room_count': room_count, 'room_messages' : room_messages}
    
    return render(request, 'base/home.html', context)



def room(request, pk):
    room = Room.objects.get(id=pk)                                                  #procura um objeto do modelo Room que possua a primary key passada
    room_messages = room.message_set.all()                    #nesse caso, message_set se refere ao conjunto do modelo message relacionado ao objeto room retornado pela linha acima
    
    participants = room.participants.all().order_by('username')

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    
    context = {'room': room, 'room_messages': room_messages, 'participants' : participants}                             #context é um dicionário com todos os dados que serão passados para o html
    return render(request, 'base/room.html', context)                               #renderiza o html 'base/room' passando a requisição e o dicionário com os itens criados


def user_profile(request, pk):
    user = User.objects.get(id=pk)
    userProfile = UserProfile.objects.get(user__id = user.id)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user' : user, 'rooms' : rooms, 'room_messages' : room_messages, 'topics' : topics, 'userProfile' : userProfile}
    return render(request, 'base/profile.html', context)


@login_required(login_url='/login')
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        room = Room(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        room.save()
        room.participants.add(request.user)
        room.save()
        
        return redirect('home')
    context = {'form' : form, 'topics' : topics}
    return render(request, 'base/room_form.html', context)

    
    context = {'form' : form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='/login')
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse("Only hosts can update their own rooms.")

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.topic = topic
        room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='/login')
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("Only hosts can delete their own rooms.")

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})


@login_required(login_url='/login')
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("Only the user that created the message can delete it.")

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':message})



@login_required(login_url='/login')
def update_user(request):
    user = request.user
    userProfile = UserProfile.objects.get(user__username = user)

    if request.method == 'POST':
        name = request.POST.get('username')
        email = request.POST.get('email')
        about = request.POST.get('about')
        avatar = request.FILES.get('avatar')

        valid = True

        if len(name) == 0:
            name = userProfile.name
        elif len(name) < 2:
            messages.error(request, 'The name has to be at least 2 character long')
            valid = False
        
        if len(email) == 0:
            email = userProfile.user.email
        elif not re.search(r'[\w.]+\@[\w.]+', email):
            messages.error(request, 'Please enter a valid Email')
            valid = False

        if len(about) == 0:
            about = userProfile.about
        elif len(about) < 10:
            messages.error(request, 'The about section has to be at least 10 character long')
            valid = False

        print(avatar)

        if not avatar:
            avatar = userProfile.avatar

        if valid == True:
            userProfile.name = name
            userProfile.user.email = email
            userProfile.about = about
            userProfile.avatar = avatar

            userProfile.save()
            userProfile.user.save()
    
    
    context = {}
    return render(request, 'base/update_user.html', context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    room_count = Room.objects.all().count
    topics = Topic.objects.alias(nroom=Count('room')).order_by('-nroom').filter(name__icontains=q)[0:5]
    context = {'room_count': room_count, 'topics': topics}
    return render(request, 'base/topics.html', context)


def activityPage(request):
    room_messages = Message.objects.all()
    context = {'room_messages':room_messages}
    return render(request, 'base/activity.html', context)
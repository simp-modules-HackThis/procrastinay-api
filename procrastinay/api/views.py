from django.shortcuts import render, get_object_or_404
from django.db import transaction
from django.contrib.auth import authenticate, login as django_login
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.forms.models import model_to_dict
from django.views.generic import View
from .models import User
from .utils import *
from importlib import import_module
from django.contrib.sessions.middleware import SessionMiddleware


def login(request: HttpRequest):
    data = request_data(request)
    username = data.get('username', None)
    email = data.get('email', None)
    password = data.get('password', None)
    class_name = data.get('class', None)
    first_name = data.get('first_name', None)
    last_name = data.get('last_name', None)

    # try to authenticate
    user = authenticate(request, username=username, password=password)
    if user != None:
        # if auth successful then login and we're done
        django_login(request, user)
    elif request.method == 'POST':  # if we want to create account do it
        # email = None
        try:
            user = User.objects.create_user(
                username, email, password, first_name=first_name or '', last_name=last_name or '', class_name=class_name)
        except Exception as e:  # Error in create_user, usually a common username
            print(f'error creating account: {e}')
            return JsonResponse({'error': 'An error occured while creating the account.'}, status=400)
    else:  # invalid user/pass
        return JsonResponse({'error': 'Invalid username or password.'}, status=400)

    request.session.save()  # again, need to save session to generate token
    json = json_user(user)
    json['token'] = request.session.session_key
    return JsonResponse(json, status=201 if request.method == 'POST' else 200)


@protected
def me(request, user):
    return JsonResponse(json_user(user))


@protected
def me_invites(request, user):
    if request.method == 'POST':
        data = request_data(request)
        guild_id = data.get('id', None)
        with transaction.atomic():
            guild = get_object_or_404(user.invites, guild_id=guild_id)
            user.invites.remove(guild)
            user.guilds.add(guild)
    return JsonResponse({
        'invites': list(user.invites.all().values_list('guild_id', flat=True))
    }, status=201 if request.method == 'POST' else 200)

@protected
def me_guilds(request: HttpRequest, user):
    if request.method == 'POST':
        data=request_data(request)
        name=data.get('name', None)
        with transaction.atomic():
            guild=Guild(name=name or '', dictator=user)
            guild.save()
            user.guilds.add(guild)
    return JsonResponse({
        'guilds': [json_guild(guild) for guild in user.guilds.all()]
    }, status=201 if request.method == 'POST' else 200)

def me_class(request: HttpRequest, user):
    if request.method == 'POST':
        data=request_data(request)
        class_name=data.get('class', None)
        with transaction.atomic():
            user.class_name=class_name
            user.save()
    return JsonResponse({
        'class': user.class_name
    }, status=201 if request.method == 'POST' else 200)

@protected
def me_tasks(request: HttpRequest, user):
    if request.method == 'POST':
        data=request_data(request)
        title=data.get('title', None)
        info=data.get('info', None)
        minutes=data.get('time', None)
        deadline=data.get('deadline', None)
        with transaction.atomic():
            UserTask(title=title or '',
                      info=info or '',
                      minutes=minutes,
                      deadline=deadline,
                      owner=user).save()


    return JsonResponse({
        'tasks': [json_task(task) for task in UserTask.objects.filter(owner=user).all()]
    }, 201 if request.method == 'POST' else 200)


@protect_guild
def guild_tasks(request: HttpRequest, user, guild):
    if request.method == 'POST':
        data=request_data(request)
        title=data.get('title', None)
        info=data.get('info', None)
        minutes=data.get('time', None)
        deadline=data.get('deadline', None)
        with transaction.atomic():
            GuildTask(title=title or '',
                      info=info or '',
                      minutes=minutes,
                      deadline=deadline,
                      creator=user,
                      owner=guild).save()

    return JsonResponse({
        'tasks': [json_task(task) for task in GuildTask.objects.filter(owner=guild).all()]
    }, 201 if request.method == 'POST' else 200)


@protected
def guild_info(request: HttpRequest, _user, guild_id):
    # TODO
    return JsonResponse(json_guild(get_object_or_404(Guild, guild_id=guild_id)))

@protect_guild
def guild_invites(request, user, guild):
    status = 200
    if request.method == 'POST' and guild.dictator == user:
        status = 201
        data = request_data(request)
        invited_user_id = data.get('id', None)
        with transaction.atomic():
            invited_user = get_object_or_404(User.objects.exclude(guilds=guild), user_id=invited_user_id)
            invited_user.invites.add(guild)
    return JsonResponse({
        'invites': list(user.invites.all().values_list('guild_id', flat=True))
    }, status=status)

@protected
def user_info(request: HttpRequest, _user, user_id):
    return JsonResponse(json_user(get_object_or_404(User, user_id=user_id)))


def classes(request: HttpRequest):
    return JsonResponse({
        'classes': [
            class_dict('Ranger', 'Ranger class description'),
            class_dict('Paladin', 'Paladin class description'),
            class_dict('Priest', 'Priest class description'),
            class_dict('Berserker', 'Berserker class description')
        ]
    })

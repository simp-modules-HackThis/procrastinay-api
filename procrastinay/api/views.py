from django.shortcuts import render
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

    # try to authenticate
    user = authenticate(request, username=username, password=password)
    if user != None:
        # if auth successful then login and we're done
        django_login(request, user)
    elif request.method == 'POST':  # if we want to create account do it
        # email = None
        try:
            user = User.objects.create_user(
                username, email, password, first_name=username)
        except Exception as e:  # Error in create_user, usually a common username
            return JsonResponse({'error': 'An error occured while creating the account.'}, status=400)
    else:  # invalid user/pass
        return JsonResponse({'error': 'Invalid username or password.'}, status=400)

    request.session.save()  # again, need to save session to generate token
    json = json_user(user)
    json['token'] = request.session.session_key
    return JsonResponse(json, status=201)


@protected
def me(request, user):
    return JsonResponse(json_user(user))


@protected
def me_guilds(request: HttpRequest, user):
    if request.method == 'POST':
        data = request_data(request)
        name = data.get('name', None)
        with transaction.atomic():
            guild = Guild(name=name or '')
            guild.save()
            user.guilds.add(guild)
    return JsonResponse({
        'guilds': [json_guild(guild) for guild in user.guilds.all()]
    }, status=201 if request.method == 'POST' else 200)


@protected
def me_tasks(request: HttpRequest, user):
    if request.method == 'POST':
        data = request_data(request)
        title = data.get('title', None)
        info = data.get('info', None)
        minutes = data.get('time', None)
        deadline = data.get('deadline', None)
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
        data = request_data(request)
        title = data.get('title', None)
        info = data.get('info', None)
        minutes = data.get('time', None)
        deadline = data.get('deadline', None)
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
    return JsonResponse(json_guild(Guild.objects.get(guild_id=guild_id)))


@protected
def user_info(request: HttpRequest, _user, user_id):
    return JsonResponse(json_user(User.objects.get(user_id=user_id)))


def classes(request: HttpRequest):
    return JsonResponse({
        'classes': [
            class_dict('Ranger', 'Ranger class description'),
            class_dict('Paladin', 'Paladin class description'),
            class_dict('Priest', 'Priest class description'),
            class_dict('Berserker', 'Berserker class description')
        ]
    })

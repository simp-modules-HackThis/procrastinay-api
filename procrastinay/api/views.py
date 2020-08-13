from django.shortcuts import render
from django.db import transaction
from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.forms.models import model_to_dict
from django.views.generic import View
from .models import User
from .utils import *
from importlib import import_module
from django.contrib.sessions.middleware import SessionMiddleware


def login(self, request: HttpRequest):
    data = request_data(request)
    username = data.get('username', None)
    email = data.get('email', None)
    password = data.get('password', None)

    # try to authenticate
    user = authenticate(request, username=username, password=password)
    if user != None:
        # if auth successful then login and we're done
        login(request, user)
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
    return JsonResponse(json)


@protected
def me(request):
    return JsonResponse(json_user(request.user))


@protected
def me_guilds(request: HttpRequest):
    if request.method == 'POST':
        data = request_data(request)
        name = data.get('name', None)
        with transaction.atomic():
            guild = Guild(name=name or '')
            guild.save()
            request.user.guilds.add(guild)
    return JsonResponse({
        'guilds': [json_guild(guild) for guild in request.user.guilds.all()]
    })


@protected
def me_tasks(request: HttpRequest):
    if request.method == 'POST':
        data = request_data(request)
        title = data.get('title', None)
        info = data.get('info', None)
        with transaction.atomic():
            UserTask(title=title or '', info=info or '',
                     owner=request.user).save()

    return JsonResponse({
        'tasks': [json_task(task) for task in UserTask.objects.filter(owner=request.user).all()]
    })


@protect_guild
def guild_tasks(request: HttpRequest, guild):
    if request.method == 'POST':
        data = request_data(request)
        title = data.get('title', None)
        info = data.get('info', None)
        with transaction.atomic():
            GuildTask(title=title or '', info=info or '', owner=guild).save()

    return JsonResponse({
        'tasks': [json_task(task) for task in GuildTask.objects.filter(owner=guild).all()]
    })


@protected
def guild_info(request: HttpRequest, guild_id):
    # TODO
    return JsonResponse(json_guild(Guild.objects.get(guild_id=guild_id)))


@protected
def user_info(request: HttpRequest, user_id):
    return JsonResponse(json_user(User.objects.get(user_id=user_id)))

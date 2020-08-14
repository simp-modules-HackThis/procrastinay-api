from .models import *
from django.utils.text import slugify
from functools import wraps
from django.http import JsonResponse, HttpRequest, HttpResponse
import json

def protect_guild(view_func):
    @wraps(view_func)
    def _protected(request, guild_id, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                guild = request.user.guilds.get(guild_id=guild_id)
            except Guild.DoesNotExist:
                return HttpResponse(status=404)
            if guild != None:
                return view_func(request, request.user, guild, *args, **kwargs)
        return HttpResponse(status=403)
    return _protected

def protected(view_func):
    @wraps(view_func)
    def _protected(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, request.user, *args, **kwargs)
        return HttpResponse(status=403)
    return _protected

def json_guild(guild: Guild):
    return {
        'id': guild.guild_id,
        'name': guild.name,
        'tasks': [json_task(task) for task in GuildTask.objects.filter(owner=guild)],
        'users': list(User.objects.filter(guilds=guild).values_list('user_id', flat=True)),
        'invites': list(User.objects.filter(invites=guild).values_list('user_id', flat=True))
    }


def json_task(task: Task):
    val = {
        'id': task.task_id,
        'title': task.title,
        'info': task.info,
        'time': task.minutes,
        'deadline': task.deadline,
    }
    if isinstance(task, GuildTask):
        val['creator'] = task.creator
    return val


def json_user(user: User):
    return {
        'id': user.user_id,
        'email': user.email,
        'join': user.date_joined,
        'class': user.class_name,
        'guilds': list(user.guilds.values_list('guild_id', flat=True)),
        'tasks': [json_task(task) for task in UserTask.objects.filter(owner=user)],
        'invites': list(user.invites.values_list('guild_id', flat=True)),
        'first_name': user.first_name,
        'last_name': user.last_name
    }


def request_data(request: HttpRequest):
    try:
        return json.loads(request.body)
    except Exception:
        return {}


def class_dict(pretty, description, name=None):
    return {
        'pretty': pretty,
        'name': name or slugify(pretty),
        'description': description
    }

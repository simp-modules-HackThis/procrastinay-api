from django.shortcuts import render
from django.contrib.auth import authenticate
from django.http import JsonResponse, HttpRequest
from django.forms.models import model_to_dict
from django.views.generic import View
from .models import User
import json


def user_to_json(user: HttpRequest):
    return {
        'id': user.user_id,
        'email': user.email,
        'join': user.date_joined,
        'guilds': [group.id for group in user.guilds.all()]
    }


def me(request):
    user = authenticate(username='matas', password='hi')
    return JsonResponse(user_to_json(user))


def user_profile(request: HttpRequest, user_id):
    user = User.objects.get(user_id=user_id)
    return JsonResponse(user_to_json(user))


def create(request: HttpRequest) -> User:

    data = json.loads(request.body or '{}')
    name = data['username']
    password = data['password']

    # email = None
    user = User.objects.create_user(name, None, password, first_name=name)
    return JsonResponse({'success': True, 'id': user.user_id})

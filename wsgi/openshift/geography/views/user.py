# -*- coding: utf-8 -*-
from geography.utils import JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.models import User


def user_list_view(request):
    users = User.objects.all()
    response = [s.to_serializable() for s in users
                if not s.is_lazy()]
    return JsonResponse(response)


def user_view(request):
    user = request.user
    if user and User.objects.is_lazy(user) and User.objects.is_named(user):
        User.objects.convert_lazy_user(request.user)
    username = user.username if user and not User.objects.is_lazy(user) else ''
    points = 0  # TODO
    response = {
        'username': username,
        'points': points,
    }
    return JsonResponse(response)


def logout_view(request):
    logout(request)
    return user_view(request)

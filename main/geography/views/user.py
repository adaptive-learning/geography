# -*- coding: utf-8 -*-
from geography.utils import JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.models import User
import geography.models.user


def user_list_view(request):
    users = User.objects.all()
    response = [geography.models.user.to_serializable(s) for s in users
                if not geography.models.user.is_lazy(s)]
    return JsonResponse(response)


def get_user(request):
    user = request.user
    if user and geography.models.user.is_lazy(user) and geography.models.user.is_named(user):
        geography.models.user.convert_lazy_user(request.user)
    username = user.username if user and not geography.models.user.is_lazy(user) else ''
    points = geography.models.user.get_points(user) if user else 0
    response = {
        'username': username,
        'points': points,
        'email': user.email if username != '' else None,
    }
    return response


def user_view(request):
    response = get_user(request)
    return JsonResponse(response)


def logout_view(request):
    logout(request)
    return user_view(request)

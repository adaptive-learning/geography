# -*- coding: utf-8 -*-
from geography.utils import JsonResponse
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.http import Http404
import geography.models.user


def user_list_view(request):
    users = User.objects.all()
    response = [geography.models.user.to_serializable(s) for s in users
                if not geography.models.user.is_lazy(s)]
    return JsonResponse(response)


def get_user(request, username=None):
    if not username:
        user = request.user
    else:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404(u"Invalid username: {0}".format(username))
    if user and geography.models.user.is_lazy(user) and geography.models.user.is_named(user):
        geography.models.user.convert_lazy_user(request.user)
    username = user.username if user and not geography.models.user.is_lazy(user) else ''
    points = geography.models.user.get_points(user) if user else 0
    response = {
        'username': username,
        'points': points,
        'email': user.email if username != '' and username == request.user.username else None,
        'first_name': user.first_name if username != '' else None,
        'last_name': user.last_name if username != '' else None,
    }
    return response


def user_view(request, username=None):
    response = get_user(request, username)
    return JsonResponse(response)


def logout_view(request):
    logout(request)
    return user_view(request)

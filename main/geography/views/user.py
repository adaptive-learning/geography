# -*- coding: utf-8 -*-
from geography.utils import JsonResponse
from django.utils import simplejson
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.http import Http404
import geography.models.user
from geography.models.user import UserProfile
from django.utils.translation import ugettext as _
from lazysignup.decorators import allow_lazy_user


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
    answered_count = geography.models.user.get_answered_count(user) if user else 0
    response = {
        'username': username,
        'points': points,
        'answered_count': answered_count,
        'email': user.email if username != '' and username == request.user.username else None,
        'first_name': user.first_name if username != '' else None,
        'last_name': user.last_name if username != '' else None,
        'send_emails': UserProfile.objects.get_profile(user).send_emails if username != '' else False,
    }
    return response


def user_view(request, username=None):
    response = get_user(request, username)
    return JsonResponse(response)


def logout_view(request):
    logout(request)
    return user_view(request)


def login_view(request):
    if request.raw_post_data:
        credentials = simplejson.loads(request.raw_post_data)
        user = authenticate(
            username=credentials.get('username', ''),
            password=credentials.get('password', ''),
        )
        if user is not None:
            if user.is_active:
                login(request, user)
                return user_view(request)
            else:
                response = {
                    'msg': _("Heslo je správné, ale účet není aktivovaný."),
                    'type': 'danger',
                }
                return JsonResponse(response, status=401)
        else:
            response = {
                'msg': _(u"Nesprávné jméno nebo heslo"),
                'type': 'danger',
            }
            return JsonResponse(response, status=401)


@allow_lazy_user
def signup_view(request):
    if request.raw_post_data:
        credentials = simplejson.loads(request.raw_post_data)
        msg = None
        if 'username' not in credentials:
            msg = _(u"Je nutné vyplnit uživatelské jméno.")
        elif 'email' not in credentials:
            msg = _(u"Je nutné vyplnit email.")
        elif 'password' not in credentials:
            msg = _(u"Je nutné vyplnit heslo.")
        elif ('passwordAgain' not in credentials
                or credentials['password'] != credentials['passwordAgain']):
            msg = _(u"Hesla se neshodují.")
        if msg is not None:
            response = {
                'msg': msg,
                'type': 'danger',
            }
            return JsonResponse(response, status=400)
        else:
            user = request.user
            user.username = credentials['username']
            user.email = credentials['email']
            user.set_password(credentials['password'])
            user.save()
            return user_view(request)


def user_save(request):
    if request.raw_post_data:
        user = request.user
        user_data = simplejson.loads(request.raw_post_data)
        user.first_name = user_data["first_name"]
        user.last_name = user_data["last_name"]
        user.email = user_data["email"]
        user.save()
        profile = UserProfile.objects.get_profile(user)
        profile.send_emails = user_data["send_emails"]
        profile.save()

    return user_view(request)

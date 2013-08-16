# -*- coding: utf-8 -*-

from core.models import Student
from core.utils import JsonResponse
from lazysignup.models import LazyUser
from django.contrib.auth import logout
from django.contrib.auth.models import User

# Create your views here.


def user_list_view(request):
    students = Student.objects.all()
    response = [s.toSerializable() for s in students if not is_lazy_user(s.user)]
    return JsonResponse(response)
    
def user_view(request):
    student = Student.fromUser(request.user)
    if(is_lazy_user(request.user) and request.user.first_name != '' and request.user.last_name != ''):
        convert_lazy_user(request.user)
    username = student.user.username if student != None and not is_lazy_user(request.user) else ''
    points = student.points if student != None else 0
    response = {
        'username' : username,
        'points' :  points ,
    }
    return JsonResponse(response)

def logout_view(request):
    logout(request)
    return user_view(request)

def convert_lazy_user(user):
    LazyUser.objects.filter(user=user).delete()
    user.username = get_unused_username(user)
    user.save()

def get_unused_username(user):
    condition = True
    append = ""
    i = 2
    while condition:
        username = user.first_name + user.last_name + append;
        condition = username_present(username)
        append = '{0}'.format(i)
        i = i+1
    return username

def username_present(username):
    if User.objects.filter(username=username).count():
        return True
    
    return False

def is_lazy_user(user):
    """ Return True if the passed user is a lazy user. """
    # Anonymous users are not lazy.
    if user.is_anonymous():
        return False

    if len(user.username) != 30 :
        return False

    # Otherwise, we have to fall back to checking the database.
    return bool(LazyUser.objects.filter(user=user).count() > 0)

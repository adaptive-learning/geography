# -*- coding: utf-8 -*-

from core.models import Student
from core.utils import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.utils import simplejson
from lazysignup.decorators import allow_lazy_user
from lazysignup.utils import is_lazy_user


# Create your views here.


@allow_lazy_user
def user_list_view(request):
    students = Student.objects.all()
    response = [s.toSerializable() for s in students if not is_lazy_user(s.user)]
    return JsonResponse(response)
    
@allow_lazy_user
def user_view(request):
    student = Student.fromUser(request.user)
    isRegistredUser = not is_lazy_user(request.user)
    username = student.user.username if isRegistredUser else ''
    response = {
        'username' : username,
        'points' :  student.points,
    }
    return JsonResponse(response)

def login_view(request):
    if (request.raw_post_data != ""):
        credentials = simplejson.loads(request.raw_post_data)
        user = authenticate(
            username=credentials["username"],
            password=credentials["password"],
        )
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
                response = {
                    'success' : True,
                    'message' : 'Uživatel {0} byl přihlášen'.format(user.username)
                    }
            else:
                # Return a 'disabled account' error message
                response = {
                    'success' : False,
                    'message' : 'Přihlašovací údaje jsou správné, ale účet je zablokován'
                }
        else:
            # Return an 'invalid login' error message.
            response = {
                'success' : False,
                'message' : 'Nesprávné uživatelské jméno nebo heslo.'
            }
    return JsonResponse(response)
    
def logout_view(request):
    logout(request)
    return user_view(request)
    
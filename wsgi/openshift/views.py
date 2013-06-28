import os
from django.shortcuts import render_to_response

def home(request):
    request.META["CSRF_COOKIE_USED"] = True
    return render_to_response('home/home.html')

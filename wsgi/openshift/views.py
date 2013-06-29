import os
from django.shortcuts import render_to_response
from django.core.context_processors import csrf

def home(request):
    request.META["CSRF_COOKIE_USED"] = True
    c = {}
    c.update(csrf(request))
    return render_to_response('home/home.html', c)

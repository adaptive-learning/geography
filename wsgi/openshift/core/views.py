# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.context_processors import csrf
from django.shortcuts import render_to_response


# Create your views here.
def home(request):
    request.META["CSRF_COOKIE_USED"] = True
    title = 'Loc - ' if not settings.ON_OPENSHIFT else ''
    c = {
         'title' : title,
         'isProduction' : settings.ON_OPENSHIFT,
    }
    c.update(csrf(request))
    return render_to_response('home/home.html', c)



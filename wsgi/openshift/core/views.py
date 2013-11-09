# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from core.utils import JsonResponse, StaticFiles
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.http import HttpResponse
from core.models import Place
import json
import os
from django.core.servers.basehttp import FileWrapper


# Create your views here.
def home(request):
    JS_FILES = (
        "static/lib/js/jquery-2.0.2.min.js",
        "static/lib/js/jquery.colorbox-min.js",
        "static/lib/js/bootstrap.js",
        "static/lib/angular/angular.min.js",
        "static/lib/angular/angular-cookies.js",
        "static/lib/js/raphael.js",
        "static/lib/js/kartograph.js",
        "static/lib/js/chroma.min.js",
        "static/lib/js/jquery.qtip.min.js",
        "static/js/map.js",
        "static/js/app.js",
        "static/js/controllers.js",
        "static/js/services.js",
        "static/js/filters.js",
        "static/js/directives.js"
    )
    TOP_CSS_FILES = (
        "static/lib/css/bootstrap.css",
        "static/css/app.css",
    )
    BOTTOM_CSS_FILES = (
        "static/lib/css/flags.css",
        "static/lib/css/tips.css",
        "static/css/map.css"
    )
    request.META["CSRF_COOKIE_USED"] = True
    title = 'Loc - ' if not settings.ON_OPENSHIFT else ''
    c = {
        'title': title,
        'isProduction': settings.ON_OPENSHIFT,
        'top_css_files': StaticFiles.add_hash(TOP_CSS_FILES),
        'bottom_css_files': StaticFiles.add_hash(BOTTOM_CSS_FILES),
        'js_files': StaticFiles.add_hash(JS_FILES),
        'continents': Place.objects.get_continents(),
        'hashes': json.dumps(settings.HASHES),
    }
    c.update(csrf(request))
    return render_to_response('home/home.html', c)


def cachedlog_view(request):
    logname = "export.json"
    logpath = os.path.join(settings.MEDIA_ROOT, logname)
    response = HttpResponse(FileWrapper(open(logpath)), content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=answers.json'
    return response


def export_view(request):
    if not request.user.is_staff:
        response = {
            "error": "Permission denied: you need to be staff member. If you think you should be able to access logs, contact admins."}
        return JsonResponse(response)
    type_key = request.GET[
        'model'] if 'model' in request.GET else 'questions.answer'
    [app_label, model] = type_key.split(".")
    try:
        ct = ContentType.objects.get_by_natural_key(app_label, model)
    except ContentType.DoesNotExist:
        return JsonResponse({"error": "Invalid model name: '%s'" % (type_key)})
    objects = ct.model_class().objects
    if 'ids' in request.GET:
        ids = request.GET['ids'].split(",")
        queryset = objects.filter(pk__in=ids)
    else:
        queryset = objects.all()
    response = HttpResponse(content_type="application/json")
    serializers.serialize("json", queryset, stream=response)
    return response

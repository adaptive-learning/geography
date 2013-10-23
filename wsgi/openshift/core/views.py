# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from core.utils import JsonResponse, StaticFiles
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.http import HttpResponse


# Create your views here.
def home(request):
    request.META["CSRF_COOKIE_USED"] = True
    title = 'Loc - ' if not settings.ON_OPENSHIFT else ''
    c = {
        'title': title,
        'isProduction': settings.ON_OPENSHIFT,
        'css_files': StaticFiles.add_hash(settings.CSS_FILES),
        'js_files': StaticFiles.add_hash(settings.JS_FILES),
    }
    c.update(csrf(request))
    return render_to_response('home/home.html', c)


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

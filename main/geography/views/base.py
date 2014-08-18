# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.context_processors import csrf
from django.shortcuts import render_to_response
from geography.utils import JsonResponse, StaticFiles
from geography.views import get_user
from django.http import HttpResponse
from geography.models import Place
import json
import os
from django.core.servers.basehttp import FileWrapper
from django.utils.translation import ugettext as _


def home(request):
    JS_FILES = (
        "/static/dist/js/fallbacks.min.js",
        "/static/dist/js/libs.min.js",
        "/static/dist/js/blind-maps.min.js",
        "/static/lib/angular-1.2.9/i18n/angular-locale_cs.js",
    )
    CSS_FILES = (
        "/static/lib/css/bootstrap.min.css",
        "/static/css/app.css",
        "/static/css/map.css"
    )
    request.META["CSRF_COOKIE_USED"] = True
    if settings.ON_PRODUCTION:
        title = ''
    elif settings.ON_STAGING:
        title = 'Stage - '
    else:
        title = 'Loc - '
    hashes = dict((key, value)
                  for key, value
                  in settings.HASHES.iteritems()
                  if "/lib/" not in key and "/js/" not in key and "/sass/" not in key
                  )
    c = {
        'title': title + _(u'Slepé Mapy') + ' - ' +
        _(u'inteligentní aplikace na procvičování zeměpisu'),
        'isProduction': settings.ON_PRODUCTION,
        'css_files': StaticFiles.add_hash(CSS_FILES),
        'js_files': StaticFiles.add_hash(JS_FILES),
        'continents': Place.objects.get_continents(),
        'states': Place.objects.get_states_with_map(),
        'hashes': json.dumps(hashes),
        'user': get_user(request),
        'LANGUAGE_CODE': request.LANGUAGE_CODE,
        'LANGUAGES': settings.LANGUAGES,
    }
    print settings.PROJECT_DIR
    c.update(csrf(request))
    return render_to_response('home.html', c)


def csv_view(request, model):
    if not request.user.is_staff:
        response = {
            "error": "Permission denied: you need to be staff member. If you think you should be able to access logs, contact admins."}
        return JsonResponse(response)
    allowed_models = [
        'place',
        'placerelation',
        'ab_group',
        'ab_value',
        'answer',
        'answer_ab_values',
        'answer_options',
        'placerelation_related_places']
    if model not in allowed_models:
        response = {"error": "the requested model '" + model + "' is not valid"}
        return JsonResponse(response)
    csv_file = "geography." + model + ".zip"
    logpath = os.path.join(settings.MEDIA_ROOT, csv_file)
    response = HttpResponse(FileWrapper(open(logpath)), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=' + csv_file
    return response

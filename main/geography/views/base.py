# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render_to_response
from geography.utils import JsonResponse, StaticFiles
from geography.views import get_user
from django.http import HttpResponse
from geography.models import Place
import json
import os
from django.core.servers.basehttp import FileWrapper
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_page
from django.views.i18n import javascript_catalog


def home(request, hack=None):
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
    title = title + _(u'Slepé Mapy') + ' - ' + _(
        u'inteligentní aplikace na procvičování zeměpisu')
    hashes = dict((key, value)
                  for key, value
                  in settings.HASHES.iteritems()
                  if "/lib/" not in key and "/js/" not in key and "/sass/" not in key
                  )
    c = {
        'title': title,
        'map': get_map_from_url(hack),
        'isProduction': settings.ON_PRODUCTION,
        'css_files': StaticFiles.add_hash(CSS_FILES),
        'js_files': StaticFiles.add_hash(JS_FILES),
        'continents': Place.objects.get_continents(),
        'states': Place.objects.get_states_with_map(),
        'hashes': json.dumps(hashes),
        'user': get_user(request),
        'LANGUAGE_CODE': request.LANGUAGE_CODE,
        'LANGUAGES': settings.LANGUAGES,
        'isHomepage': hack is None,
    }
    return render_to_response('home.html', c)


def get_map_from_url(hack):
    map_string = ""
    if hack:
        url = hack.split('/')
        if url[0] == u'view' or url[0] == u'practice':
            map_code = url[1]
            try:
                map_place = Place.objects.get(code=map_code)
                map_string = map_place.name
                if len(url) >= 3 and url[2] != '':
                    map_string = map_string + ' - ' + resolve_map_type(url[2])
            except Place.DoesNotExist:
                pass
    return map_string


def resolve_map_type(place_type_slug):
    place_type = (Place.PLACE_TYPE_PLURALS[
                  Place.PLACE_TYPE_SLUGS_LOWER_REVERSE[place_type_slug]][1]
                  if place_type_slug in Place.PLACE_TYPE_SLUGS_LOWER_REVERSE
                  else Place.CATEGORIES_NAMES[place_type_slug]
                  if place_type_slug in Place.CATEGORIES
                  else '')
    return unicode(place_type)


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


@cache_page(86400)
def cached_javascript_catalog(request, domain='djangojs', packages=None):
    return javascript_catalog(request, domain, packages)

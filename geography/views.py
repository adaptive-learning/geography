# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render_to_response
import json
from django.utils.translation import ugettext as _
from proso_questions_client.utils import StaticFiles, get_user
from django.utils.translation import get_language
from proso.django.config import get_global_config
from proso_flashcards.models import Category
from django.views.decorators.cache import cache_page
from django.views.i18n import javascript_catalog


def home(request, hack=None):
    JS_FILES = (
        "/static/bower-libs.js",
        "/static/dist/js/bbox.js",
        "/static/dist/js/hash.js",
        "/static/js/app.js",
        "/static/js/controllers.js",
        "/static/js/filters.js",
        "/static/js/directives.js",
        "/static/js/services.js",
        "/static/js/map.js",
        "/static/proso_mnemonics/js/app.js",
        "/static/lib/angular-1.2.9/i18n/angular-locale_cs.js",
        "/static/lib/js/googleExperiments.min.js",
    )
    CSS_FILES = (
        "/static/lib/css/bootstrap.min.css",
        "/static/lib/css/xeditable.css",
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
    title = title + _(u'Slepé mapy') + ' - ' + _(
        u'inteligentní aplikace na procvičování zeměpisu')
    hashes = dict((key, value)
                  for key, value
                  in settings.HASHES.iteritems()
                  if "/lib/" not in key and "/js/" not in key and "/sass/" not in key
                  )
    user = get_user(request)
    # OpenID migration HACK
    # https://developers.google.com/identity/protocols/OpenID2Migration
    if user.__class__.__name__ == 'HttpResponseRedirect':
        return user
    # end HACK
    c = {
        'title': title,
        'map': get_map_from_url(hack),
        'isProduction': settings.ON_PRODUCTION,
        'css_files': StaticFiles.add_hash(CSS_FILES),
        'js_files': StaticFiles.add_hash(JS_FILES),
        'continents': Category.objects.filter(
            lang=get_language(), type='continent'),
        'states': Category.objects.filter(lang=get_language(), type='state'),
        'hashes': json.dumps(hashes),
        'user': user,
        'userJson': json.dumps(user),
        'LANGUAGE_CODE': get_language(),
        'LANGUAGES': settings.LANGUAGES,
        'isHomepage': hack is None,
        'config_json': json.dumps(get_global_config()),
        # 'placeTypeNames': json.dumps(dict((Place.PLACE_TYPE_SLUGS_LOWER[i[0]], _(i[1]))
        #                                   for i in Place.PLACE_TYPE_PLURALS)),
    }
    return render_to_response('home.html', c)


def get_map_from_url(hack):
    map_string = ""
    if hack:
        url = hack.split('/')
        if url[0] == u'view' or url[0] == u'practice':
            map_code = url[1]
            try:
                map_category = Category.objects.get(lang=get_language(), identifier=map_code)
                map_string = map_category.name
                if len(url) >= 3 and url[2] != '':
                    map_string = map_string  # + ' - ' + resolve_map_type(url[2])
            except Category.DoesNotExist:
                pass
    return map_string


"""
def resolve_map_type(place_type_slug):
    place_type = (Place.PLACE_TYPE_PLURALS[
                  Place.PLACE_TYPE_SLUGS_LOWER_REVERSE[place_type_slug]][1]
                  if place_type_slug in Place.PLACE_TYPE_SLUGS_LOWER_REVERSE
                  else Place.CATEGORIES_NAMES[place_type_slug]
                  if place_type_slug in Place.CATEGORIES
                  else '')
    return unicode(place_type)
"""


@cache_page(86400)
def cached_javascript_catalog(request, domain='djangojs', packages=None):
    return javascript_catalog(request, domain, packages)

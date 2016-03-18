# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render_to_response
import json
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from proso.django.config import get_global_config
from proso_flashcards.models import Category
from django.views.decorators.csrf import ensure_csrf_cookie
from proso_models.models import get_environment
from proso.django.config import get_config
from proso_user.models import migrate_google_openid_user
import django.contrib.auth as auth
from proso.django.request import is_user_id_overridden
import os
import random


@ensure_csrf_cookie
def home(request, hack=None):
    JS_FILES = (
        "dist/js/bower-libs.min.js",
        "dist/js/proso-apps-all.js",
        "dist/js/geography.min.js",
        "dist/js/geography.html.js",
    )
    CSS_FILES = (
        "dist/css/bower-libs.css",
        "dist/css/app.css",
        "dist/css/map.css"
    )
    if not hasattr(request.user, "userprofile") or request.user.userprofile is None:
        environment = get_environment()
        user = json.dumps({
            'user': {},
            'number_of_answers': environment.number_of_answers(user=request.user.id) if request.user.id is not None else 0,
            'number_of_correct_answers': environment.number_of_correct_answers(user=request.user.id) if request.user.id is not None else 0,
        })
        email = ''
    else:
        if get_config('proso_user', 'google.openid.migration', default=True) and not is_user_id_overridden(request):
            migrated_user = migrate_google_openid_user(request.user)
            if migrated_user is not None:
                auth.logout(request)
                migrated_user.backend = 'social_auth.backends.google.GoogleOAuth2Backend'
                auth.login(request, migrated_user)
        user = json.dumps(request.user.userprofile.to_json(stats=True))
        email = request.user.email
    c = {
        'title': _(u'Slepé mapy') + ' - ' + _(u'inteligentní aplikace na procvičování zeměpisu'),
        'map': get_map_from_url(hack),
        'is_production': settings.ON_PRODUCTION,
        'css_files': CSS_FILES,
        'map_files': get_map_files(),
        'js_files': JS_FILES,
        'continents': Category.objects.filter(
            lang=get_language(), type='continent').order_by('name'),
        'states': Category.objects.filter(
            lang=get_language(), type='state').order_by('name'),
        'user_json': user,
        'email': email,
        'LANGUAGE_CODE': get_language(),
        'LANGUAGES': settings.LANGUAGES,
        'LANGUAGE_DOMAINS': settings.LANGUAGE_DOMAINS if hasattr(
            settings, 'LANGUAGE_DOMAINS') else {},
        'is_homepage': hack is None,
        'hack': hack or '',
        'config_json': json.dumps(get_global_config()),
        'DOMAIN': request.build_absolute_uri('/')[:-1],
        'screenshot_files': get_screenshot_files(request, hack),
    }
    return render_to_response('home.html', c)


def get_map_files():
    path = os.path.join(settings.STATICFILES_DIRS[0], 'map')
    dirs = os.listdir(path)
    map_files = ['/static/map/' + file for file in dirs]
    return map_files


def get_screenshot_files(request, hack):
    screenshot_files = [
        "/static/img/practice-example-" + get_language() + ".png",
        "/static/img/knowledge-map.png",
        "/static/img/knowledge-map-africa.png",
        "/static/img/knowledge-map-asia.png",
        "/static/img/knowledge-map-cz-mountains.png",
    ]

    path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'thumb')
    dirs = os.listdir(path)

    for file in dirs:
        if get_language() + '.png' in file:
            screenshot_files.append('/static/img/thumb/' + file)
    random.shuffle(screenshot_files)

    if hack is not None:
        thumb_file_name = hack.replace('/', '-') + '-' + get_language() +'.png'
        thumb_file = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'thumb', thumb_file_name)
        if os.path.exists(thumb_file):
            screenshot_files[0] = "/static/img/thumb/" + thumb_file_name

    if request.GET.get('thumb', None) is not None:
        screenshot_files[0] = "/static/img/thumb/" + request.GET['thumb'] + "-" + get_language() + ".png"
    return screenshot_files[:5]


def get_map_from_url(hack):
    map_string = ""
    if hack:
        url = hack.split('/')
        if url[0] == 'view' or url[0] == 'practice':
            map_code = url[1]
            try:
                map_category = Category.objects.get(lang=get_language(), identifier=map_code)
                map_string = map_category.name
                if len(url) >= 3 and url[2] != '':
                    map_string = map_string + ' - ' + resolve_map_type(url[2])
            except Category.DoesNotExist:
                pass
    return map_string


def resolve_map_type(code):
    types = {
        'state': _(u'Státy'),
        'region': _('Regiony'),
        'province': _('Provincie'),
        'region_cz': _('Kraje'),
        'region_it': _('Oblasti'),
        'autonomous_Comunity': _(u'Autonomní společenství'),
        'bundesland': _(u'Spolkové země'),
        'city': _(u'Města'),
        'river': _(u'Řeky'),
        'lake': _('Jezera'),
        'sea': _(u'Moře'),
        'mountains': _(u'Pohoří'),
        'island': _('Ostrovy'),
    }
    return types.get(code, '')

# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render_to_response, redirect
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
from django.template import RequestContext
from django.core import management
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
import base64
from proso_user.models import UserProfile


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


@ensure_csrf_cookie
def home(request, hack=None):
    if not hasattr(request.user, "userprofile") or request.user.userprofile is None:
        environment = get_environment()
        user = json.dumps({
            'user': {},
            'number_of_answers': environment.number_of_answers(user=request.user.id) if request.user.id is not None else 0,
            'number_of_correct_answers': environment.number_of_correct_answers(user=request.user.id) if request.user.id is not None else 0,
        })
        email = ''
    else:
        if hack is None:
            return redirect('/overview/')
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
        'regions': Category.objects.filter(
            lang=get_language(), type='region').order_by('name'),
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
    map_files = ['map/' + file for file in dirs]
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
        thumb_file_name = hack.replace('/', '-').replace(
            'practice-', '').replace('view-', '') + '.png'
        thumb_file = os.path.join(
            settings.MEDIA_ROOT, 'thumbs', thumb_file_name)
        if os.path.exists(thumb_file):
            screenshot_files[0] = "/media/thumbs/" + thumb_file_name

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


def get_place_types():
    return {
        'state': _(u'Státy'),
        'region': _('Regiony'),
        'province': _('Provincie'),
        'region_cz': _('Kraje'),
        'region_it': _('Oblasti'),
        'autonomous_comunity': _(u'Autonomní společenství'),
        'bundesland': _(u'Spolkové země'),
        'city': _(u'Města'),
        'river': _(u'Řeky'),
        'lake': _('Jezera'),
        'sea': _(u'Moře'),
        'mountains': _(u'Pohoří'),
        'island': _('Ostrovy'),
        'state-by-city': _('Státy skrze hlavní města'),
        'district': _('Okresy'),
        'city-by-state': _('Hlavní města skrze státy'),
        'reservoir': _('Vodní nádrže'),
        'surface': _('Povrch'),
        'chko': _('CHKO a NP'),
        'soorp': _('Obce s rozšířenou působností'),
        'soopu': _('Obce s pověřeným obecním úřadem'),
        'mzchu': _('Maloplošná zvláště chráněná území'),
    }


def resolve_map_type(code):
    return get_place_types().get(code, '')


@staff_member_required
def load_data(request):
    c = RequestContext(request, {
        'css_files': CSS_FILES,
        'alerts': [],
    })

    if request.method == 'POST':
        if 'svg' not in request.FILES:
            c['alerts'].append({
                'text': 'Chybí SVG soubor',
                'type': 'danger',
            })
        if 'json' not in request.FILES:
            c['alerts'].append({
                'text': 'Chybí JSON soubor',
                'type': 'danger',
            })

        if len(c['alerts']) == 0:
            json_file = request.FILES['json']
            filepath = os.path.join(settings.DATA_DIR, json_file.name)
            handle_uploaded_file(json_file, filepath)

            management.call_command(
                'load_flashcards',
                filepath,
                ignored_flashcards='disable',
                skip_language_check=True,
                verbosity=0,
                interactive=False)

            svg_file = request.FILES['svg']
            filepath = os.path.join(settings.STATICFILES_DIRS[0], 'map', svg_file.name)
            handle_uploaded_file(svg_file, filepath)

            management.call_command(
                'collectstatic',
                verbosity=0,
                interactive=False)
            c['alerts'].append({
                'type': 'success',
                'text': 'Mapa byla úspěšně nahrána',
            })

    return render_to_response('load_data.html', c)


def handle_uploaded_file(f, filepath):
    destination = open(filepath, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()


def save_screenshot(request):
    if request.body:
        data = json.loads(request.body.decode("utf-8"))
        image = data['image']
        filename = os.path.join(
            settings.MEDIA_ROOT, 'thumbs', data['name'] + '.png')
        save_base64_to_file(filename, image)
        response = """{
            "type": "success",
            "msg" : "Obrázek byl úspěšně nahrán"
        }"""
        return HttpResponse(response, content_type='application/javascript')


def save_base64_to_file(filename, image):
    directory = os.path.dirname(filename)
    if not os.path.exists(directory):
        os.makedirs(directory)
    head = 'data:image/png;base64,'
    if head in image:
        image = image[len(head):]
        file_size = os.path.getsize(filename) if os.path.exists(filename) else 0
        image_encoded = base64.b64decode(image)
        if file_size < len(image_encoded):
            fh = open(filename, "wb")
            fh.write(image_encoded)
            fh.close()


def unsubscribe(request):
    profile = UserProfile.objects.get(user__email=request.GET['mail'])
    profile.send_emails = False
    profile.save()
    response = """Odhlášení problěhlo úspěšně"""
    return HttpResponse(response, content_type='application/javascript')

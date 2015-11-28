from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView
from django.http import HttpResponse

admin.autodiscover()

js_info_dict = {
    'domain': 'djangojs',
    'packages': ('geography',),
}


urlpatterns = patterns(
    '',
    url(
        r'^media/(?P<path>image/.*)$', 'django.views.static.serve',
        {
            'document_root': settings.MEDIA_ROOT
        }
    ),
    url(r'^$', 'geography.views.home', name='home'),
    url(r'^(about|overview|mistakes|goals|view/\w+|u/\w+|practice/\w+/\w*|refreshpractice/\w+/\w*)',
        'geography.views.home', name='home'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='static/img/favicon.png')),
    url(r'^robots.txt$', lambda r: HttpResponse(
        "User-agent: *\nDisallow:", content_type="text/plain")),

    url(r'^user/', include('proso_user.urls')),
    url(r'^questions/', include('proso_questions.urls')),
    url(r'^models/', include('proso_models.urls')),
    url(r'^configab/', include('proso_configab.urls')),
    url(r'^common/', include('proso_common.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^convert/', include('lazysignup.urls')),
    url(r'^feedback/', include('proso_feedback.urls')),
    url(r'^flashcards/', include('proso_flashcards.urls')),

    # legacy hack
    url(r'^login/google/$', RedirectView.as_view(url='/login/google-oauth2/')),

    url(r'', include('social_auth.urls')),
)
urlpatterns += staticfiles_urlpatterns()

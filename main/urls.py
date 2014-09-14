from django.conf.urls.defaults import patterns, include, url
from django.views.generic import RedirectView
from django.http import HttpResponse

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from sitemap import sitemaps


js_info_dict = {
    'domain': 'djangojs',
    'packages': ('geography',),
}

urlpatterns = patterns(
    '',
    url(r'^$', 'geography.views.home', name='home'),
    url(r'^(about|overview|mistakes|view/\w+|u/\w+|practice/\w+)',
        'geography.views.home', name='home'),

    url(r'', include('social_auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^convert/', include('lazysignup.urls')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),

    url(r'^usersplaces/(?P<map_code>\w+)/(?P<user>\w*)', 'geography.views.users_places', name='usersplaces'),
    url(r'^placesoverview/', 'geography.views.places_overview', name='places_overview'),
    url(r'^mapskill/(?P<user>\w*)', 'geography.views.mapskill', name='mapskill'),
    url(r'^confused/', 'geography.views.confused', name='confused'),
    url(r'^csv/(?P<model>\w*)', 'geography.views.csv_view', name='csv_view'),
    url(r'^question/(?P<map_code>\w+)/(?P<place_type_slug>\w*)', 'geography.views.question', name='question'),

    url(r'^user/list/', 'geography.views.user_list_view', name='user_list_view'),
    url(r'^user/logout/', 'geography.views.logout_view', name='logout_view'),
    url(r'^user/(?P<username>[\w\.]*)', 'geography.views.user_view', name='user_view'),

    url(r'^feedback/', 'geography.views.feedback', name='feedback'),
    url(r'^goal/delete/(?P<id>[0-9]+)', 'geography.views.goals_delete', name='goals_delete'),
    url(r'^goal/(?P<username>[\w\.]*)', 'geography.views.goals_view', name='goals_view'),

    url(r'^favicon\.ico$', RedirectView.as_view(url='static/img/favicon.png')),
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    url(r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /question/\n", mimetype="text/plain")),
)

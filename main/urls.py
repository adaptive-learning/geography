from django.conf.urls.defaults import patterns, include, url
from django.views.generic import TemplateView, RedirectView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'geography.views.home', name='home'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='static/img/favicon.png')),
    url(r'^tpl/welcome_page.html$', TemplateView.as_view(template_name="home/welcome_page.html")),
    url(r'^tpl/how_it_works.html$', TemplateView.as_view(template_name="home/how_it_works.html")),
    url(r'^tpl/about.html$', TemplateView.as_view(template_name="home/about.html")),
    url(r'', include('social_auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^usersplaces/(?P<map_code>\w+)/(?P<user>\w*)', 'geography.views.users_places', name='usersplaces'),
    url(r'^places/(?P<map_code>\w+)', 'geography.views.places', name='places'),
    url(r'^csv/(?P<model>\w*)', 'geography.views.csv_view', name='csv_view'),
    url(r'^convert/', include('lazysignup.urls')),
    url(r'^question/(?P<map_code>\w+)/(?P<place_type_slug>\w*)', 'geography.views.question', name='question'),
    url(r'^user/list/', 'geography.views.user_list_view', name='user_list_view'),
    url(r'^user/logout/', 'geography.views.logout_view', name='logout_view'),
    url(r'^user/', 'geography.views.user_view', name='user_view'),
)

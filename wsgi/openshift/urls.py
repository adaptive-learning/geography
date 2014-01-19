from django.conf.urls.defaults import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'geography.views.home', name='home'),
    url(r'^tpl/welcome_page.html$', TemplateView.as_view(template_name="home/welcome_page.html")),
    url(r'^tpl/how_it_works.html$', TemplateView.as_view(template_name="home/how_it_works.html")),
    url(r'', include('social_auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^usersplaces/(?P<map_code>\w+)/(?P<user>\w*)', 'geography.views.users_places', name='usersplaces'),
    url(r'^export/', 'geography.views.export_view', name='export_view'),
    url(r'^cachedlog/(?P<file_type>csv)', 'geography.views.cachedlog_view', name='cachedlog_view'),
    url(r'^convert/', include('lazysignup.urls')),
    url(r'^question/(?P<map_code>\w+)/(?P<place_type_slug>\w*)', 'geography.views.question', name='question'),
    url(r'^user/list/', 'geography.views.user_list_view', name='user_list_view'),
    url(r'^user/logout/', 'geography.views.logout_view', name='logout_view'),
    url(r'^user/', 'geography.views.user_view', name='user_view'),
)

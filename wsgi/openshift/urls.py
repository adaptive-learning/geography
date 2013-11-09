from django.conf.urls.defaults import patterns, include, url
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       url(r'^$', 'core.views.home', name='home'),

                       url(r'^tpl/welcome_page.html$', TemplateView.as_view(
                           template_name="home/welcome_page.html")
                           ),
                       url(r'^tpl/how_it_works.html$', TemplateView.as_view(
                           template_name="home/how_it_works.html")
                           ),

                       url(r'', include('social_auth.urls')),
                       # url(r'^openshift/', include('openshift.foo.urls')),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),

                       url(r'^usersplaces/(?P<map_code>\w+)/(?P<user>\w*)',
                           'questions.views.users_places', name='usersplaces'),
                       url(r'^export/', 'core.views.export_view',
                           name='export_view'),
                       url(r'^cachedlog/', 'core.views.cachedlog_view',
                           name='cachedlog_view'),
                       url(r'^user/', include('accounts.urls')),
                       url(r'^question/', include('questions.urls')),

                       url(r'^convert/', include('lazysignup.urls')),
                       )

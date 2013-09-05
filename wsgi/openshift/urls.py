from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from core.views import home
from questions.views import users_places

urlpatterns = patterns('',
    # Examples:
    url(r'^$', home, name='home'),
    
    url(r'', include('social_auth.urls')),
    # url(r'^openshift/', include('openshift.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^usersplaces/(?P<map_code>\w+)/(?P<user>\w*)', users_places, name='usersplaces'),
    url(r'^user/', include('accounts.urls')),
    url(r'^question/', include('questions.urls')),
    
    url(r'^convert/', include('lazysignup.urls')),
)


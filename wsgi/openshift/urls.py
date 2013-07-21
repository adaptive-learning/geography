from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from core import views

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'openshift.views.home', name='home'),
    # url(r'^openshift/', include('openshift.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    
    url(r'^places/', views.places, name='places'),
    url(r'^usersplaces/(?P<part>\w+)/(?P<user>\w*)', views.users_places, name='usersplaces'),
    url(r'^question/', views.question, name='question'),
    url(r'^user/login/', views.login_view, name='login_view'),
    url(r'^user/logout/', views.logout_view, name='logout_view'),
    url(r'^user/list/', views.user_list_view, name='user_list_view'),
    url(r'^user/', views.user_view, name='user_view'),
    url(r'^updateStates/', views.updateStates_view, name='updateStates_view'),

    url(r'^convert/', include('lazysignup.urls')),
)


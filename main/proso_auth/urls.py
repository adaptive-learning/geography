from django.conf.urls import patterns, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^list/', 'proso_auth.views.user_list_view', name='user_list_view'),
    url(r'^logout/', 'proso_auth.views.logout_view', name='logout_view'),
    url(r'^save/', 'proso_auth.views.user_save', name='user_save'),
    url(r'^login/', 'proso_auth.views.login_view', name='login_view'),
    url(r'^signup/', 'proso_auth.views.signup_view', name='signup_view'),
    url(r'^(?P<username>[\w\.]*)', 'proso_auth.views.user_view', name='user_view'),
)

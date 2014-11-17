from django.conf.urls import patterns, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^delete/(?P<id>[0-9]+)', 'proso_goals.views.goals_delete', name='goals_delete'),
    url(r'^(?P<username>[\w\.]*)', 'proso_goals.views.goals_view', name='goals_view'),
)

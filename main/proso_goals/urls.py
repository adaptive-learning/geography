from django.conf.urls import patterns, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^delete/(?P<id>[0-9]+)', 'proso_goals.views.goals_delete', name='goals_delete'),
    url(r'^debug-reminder-email/(?P<username>[\w\.]*)',
        'proso_goals.views.reminder_email', name='reminder_email'),
    url(r'^(?P<username>[\w\.]*)', 'proso_goals.views.goals_view', name='goals_view'),
)

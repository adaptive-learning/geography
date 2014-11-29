from django.conf.urls import patterns, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', 'proso_feedback.views.feedback', name='feedback'),
    url(r'^rating$', 'proso_feedback.views.rating', name='rating'),
)

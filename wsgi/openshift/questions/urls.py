try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

from questions import views

# URL patterns for lazysignup

urlpatterns = patterns('lazysignup.views',
    url(r'^(?P<map_code>\w+)', views.question, name='question'),
)

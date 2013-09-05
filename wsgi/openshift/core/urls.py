try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

from core import views

# URL patterns for lazysignup

urlpatterns = patterns('lazysignup.views',
)

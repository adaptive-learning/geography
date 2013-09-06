try:
    from django.conf.urls import patterns
except ImportError:
    from django.conf.urls.defaults import patterns


# URL patterns for lazysignup

urlpatterns = patterns('lazysignup.views',
)

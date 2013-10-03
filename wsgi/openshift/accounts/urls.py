try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

from accounts import views

# URL patterns for lazysignup

urlpatterns = patterns('lazysignup.views',
                       url(r'^$', views.user_view, name='user_view'),
                       url(r'^list/', views.user_list_view,
                           name='user_list_view'),
                       url(r'^logout/', views.logout_view, name='logout_view'),
                       )

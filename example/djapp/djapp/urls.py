from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()  # for django 1.6

urlpatterns = patterns('',  # browser oriented views
    url(r'^$', 'djapp.views.index', name='home'),
    url(r'^api/', include('djapp.apiurls')),

    url(r'^admin/', include(admin.site.urls)),
)



from django.conf.urls import patterns, url
from djapiauth.utility import url_with_auth


urlpatterns = patterns('',
    url_with_auth(r'^hello/$', 'djapp.views.index'),
    url(r'^goodbye/$', 'djapp.apis.apicall'),
)

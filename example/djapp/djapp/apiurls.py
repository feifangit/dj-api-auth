from django.conf.urls import patterns, url
from djapiauth import url_with_auth
import apis

urlpatterns = patterns('',
    url_with_auth(r'^hello/$', 'djapp.views.index'),
    url(r'^goodbye/$', 'djapp.apis.apicall'),

    url(r'^classbased1/$', apis.ProtectedView.as_view()),
    url(r'^classbased2/$', apis.UnprotectedView.as_view()),

)

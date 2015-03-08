from django.conf.urls import patterns, url
from djapiauth.utility import reg_n_protect_api, reg_api
import views as browserviews


urlpatterns = patterns('',
    reg_n_protect_api(r'^hello/$', 'index', views=browserviews),
    reg_api(r'^goodbye/$', 'djapp.apis.apicall'),
)

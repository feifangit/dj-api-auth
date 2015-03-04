from django.contrib import admin
from django.forms import ModelForm
from django.contrib.auth import get_user_model
from django import forms
from djapiauth.models import APIKeys, APIEntryPoint
from djapiauth.forms import get_api_key_form
from . import API_AUTH_ADMIN_USER_FILTER


class APIKeyForm(ModelForm):
    class Meta:
        model = APIKeys
        exclude = ()
    user = forms.ModelChoiceField(queryset=get_user_model().objects.filter(company__isnull=True),
                                  required=True,)


class APIKeysAdmin(admin.ModelAdmin):
    form = APIKeyForm
    add_form = APIKeyForm
    list_display = ('apikey', 'user', 'note')
    list_filter = ('apis',)


admin.site.register(APIEntryPoint)
admin.site.register(APIKeys,
                    form=get_api_key_form(API_AUTH_ADMIN_USER_FILTER),
                    add_form=get_api_key_form(API_AUTH_ADMIN_USER_FILTER),
                    list_display=('apikey', 'user', 'note'),
                    list_filter=('apis',))

from django.forms import ModelForm
from django.contrib.auth import get_user_model
from django import forms
from .models import APIKeys


def get_api_key_form(userfilter={}):
    """
    userfileter: when binding api key with user, filter some users if necessary
    """
    class APIKeyForm(ModelForm):
        class Meta:
            model = APIKeys
            exclude = ("apitree",)
        user = forms.ModelChoiceField(queryset=get_user_model().objects.filter(**userfilter),
                                      required=True,)
    return APIKeyForm

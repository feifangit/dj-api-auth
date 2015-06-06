import json
from django.http import HttpResponse
from django.views.generic import View

from djapiauth import api_auth
from djapiauth import AuthMixin

@api_auth
def apicall(request):
    return HttpResponse(json.dumps({"message": "goodbye"}))


class ProtectedView(AuthMixin,View):

    def get(self, request):
        return HttpResponse(json.dumps({"message": "hello, auth"}))


class UnprotectedView(AuthMixin,View):
    api_auth = False

    def get(self, request):
        return HttpResponse(json.dumps({"message": "no auth needed"}))
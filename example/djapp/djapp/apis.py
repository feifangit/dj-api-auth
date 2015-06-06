import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from djapiauth import api_auth
from djapiauth import AuthMixin

@csrf_exempt
@api_auth
def apicall(request):
    if request.method == "GET":
        return HttpResponse(json.dumps({"message": "goodbye", "method": "get"}))
    else:
        return HttpResponse(json.dumps({"message": "goodbye," + request.body, "method": "post"}))


class ProtectedView(AuthMixin, View):

    def get(self, request):
        return HttpResponse(json.dumps({"message": "hello, auth from get"}))

    def post(self, request):
        return HttpResponse(json.dumps({"message": "hello, auth from post", "body": request.body}))


class UnprotectedView(AuthMixin, View):
    api_auth = False

    def get(self, request):
        return HttpResponse(json.dumps({"message": "no auth needed"}))
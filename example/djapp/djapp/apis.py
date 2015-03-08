import json
from django.http import HttpResponse
from djapiauth.auth import api_auth


@api_auth
def apicall(request):
    return HttpResponse(json.dumps({"message": "goodbye"}))


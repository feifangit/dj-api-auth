import uuid
import re
import cPickle
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AnonymousUser


class APIEntryPoint(models.Model):
    class Meta:
        verbose_name = "Entry point"
    name = models.CharField(max_length=100, unique=True)
    pattern = models.CharField(max_length=100)  # cPickle.dumps(<compiled RE>)

    def __unicode__(self):
        return unicode(self.name)


def gen_apikey():  # django 1.7 can not serilize lambda funciton
    return uuid.uuid4().hex[:8]


def gen_seckey():  # django 1.7 can not serilize lambda funciton
    return uuid.uuid4().hex


class APIKeys(models.Model):
    class Meta:
        verbose_name = "Credential"

    apikey = models.CharField(max_length=50, default=gen_apikey, unique=True)
    seckey = models.CharField(max_length=50, default=gen_seckey)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL)
    apis = models.ManyToManyField(APIEntryPoint, blank=True, null=True, help_text="accessible api entries")
    note = models.CharField(max_length=80, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.apikey)

    @staticmethod
    def permission_check(apikey, endpoint):
        """
        return (user, seckey) if url end point is in allowed entry point list
        """
        try:
            # todo performance
            r = APIKeys.objects.get(apikey=apikey)
            for api in r.apis.all():
                regexlist = cPickle.loads(api.pattern.encode("ascii"))
                path = endpoint

                for _regex in regexlist:  # for each url parts, try to match
                    match = _regex.search(path)
                    if match:
                        path = path[match.end():]  # partial match, try to match the rest
                        if not path:  # fully matched
                            return r.user if r.user else AnonymousUser(), r.seckey
                    else:
                        break
        except APIKeys.DoesNotExist:
            pass
        return None, None

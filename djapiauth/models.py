import uuid
import re
import cPickle
import pprint

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db.models.signals import m2m_changed, pre_delete
from django.dispatch import receiver


class APITree(object):
    def __init__(self):
        self._tree = {}  # re name -> (redump, sub dict)
    
    def add(self, srelist):
        p = self._tree
        for sre in srelist:
            pr = sre.pattern
            if not p.has_key(pr):
                p[pr] = (sre, {})
            p = p[pr][1]

    def pprint(self):
        pprint.pprint(self._tree)

    def match(self, url):
        path = url
        eps = self._tree  # entry points at same level
        bpartialmatch = True
        while eps and bpartialmatch:  # until leaf
            bpartialmatch = False
            for rename, (redump, nextlevel) in eps.items():
                match = redump.search(path)
                if match:
                    path, eps, bpartialmatch = path[match.end():], nextlevel, True
                    if (not path) and (not eps):  # perfect match
                        return True
                    break  # partial match, jump to next level
                else:  # not match for this entry, try next one at same level
                    continue

            if not bpartialmatch:  # failed to match in this level
                return False 
        return False



class APIEntryPoint(models.Model):
    class Meta:
        verbose_name = "Entry point"
    name = models.CharField(max_length=100, unique=True)
    pattern = models.CharField(max_length=300)  # cPickle.dumps(<compiled RE>)

    def __unicode__(self):
        return unicode(self.name)


def gen_apikey():  # django 1.7 can not serilize lambda funciton
    return uuid.uuid4().hex[:8]


def gen_seckey():  # django 1.7 can not serilize lambda funciton
    return uuid.uuid4().hex

def gen_empty_list():
    return cPickle.dumps([])

class APIKeys(models.Model):
    class Meta:
        verbose_name = "Credential"

    apikey = models.CharField(max_length=50, default=gen_apikey, unique=True)
    seckey = models.CharField(max_length=50, default=gen_seckey)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL)
    apis = models.ManyToManyField(APIEntryPoint, blank=True, null=True, help_text="accessible api entries")
    note = models.CharField(max_length=80, null=True, blank=True)
    apitree = models.TextField(default=gen_empty_list)

    def __unicode__(self):
        return unicode(self.apikey)

    @staticmethod
    def permission_check(apikey, endpoint):
        """
        return (user, seckey) if url end point is in allowed entry point list
        """
        try:
            ak = APIKeys.objects.get(apikey=apikey)
            apitree = cPickle.loads(ak.apitree.encode("ascii"))
            if apitree.match(endpoint):
                return ak.user if ak.user else AnonymousUser(), ak.seckey
        except APIKeys.DoesNotExist:
            pass
        return None, None

def _api_set_changed(sender, instance, action, **kwargs):
    # removed/add an API from an API key
    tree = APITree()
    if action == "post_clear":
        instance.apitree = cPickle.dumps(tree)
        instance.save(update_fields=["apitree"])
    elif (action == "post_remove" or action == "post_add"):
        for api in instance.apis.all():
            srelist = cPickle.loads(api.pattern.encode("ascii"))
            tree.add(srelist)
        instance.apitree = cPickle.dumps(tree)
        instance.save(update_fields=["apitree"])

m2m_changed.connect(_api_set_changed, sender=APIKeys.apis.through)

@receiver(pre_delete, sender=APIEntryPoint)
def _api_entry_deleted(sender, instance, using, *args, **kwargs):
    # when an api entry is deleted, 
    # the entry will be removed automatically from api key
    # but we need to refresh the apitree field which stores the data strucuture for fast-matching
    for apikey in instance.apikeys_set.all():
        tree = APITree()

        for api in apikey.apis.all():
            if api.id == instance.id:
                continue
            srelist = cPickle.loads(api.pattern.encode("ascii"))
            tree.add(srelist)
        apikey.apitree = cPickle.dumps(tree)
        apikey.save(update_fields=["apitree"])

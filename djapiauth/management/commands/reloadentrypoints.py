# -*- coding: utf-8 -*-
import cPickle
from django.core.management.base import BaseCommand, CommandError
from django.utils.module_loading import import_by_path
from django.conf import settings

from ...models import APIEntryPoint
from ...utility import is_protected_api, traverse_urls

rooturl = import_by_path(settings.ROOT_URLCONF+".urlpatterns")


class Command(BaseCommand):
    args = ''
    help = 'add missed endpoint'

    def handle(self, *args, **options):
        currAEP = set([aep.name.encode("ascii") for aep in APIEntryPoint.objects.all()])  # current entries in db
        newDiscovered = set()

        def _save_reg_api(u, prefixre, prefixname):
            if is_protected_api(u):
                urldisplayname = " ".join(prefixname + [u._regex,])

                newDiscovered.add(urldisplayname)
                obj, bCreated = APIEntryPoint.objects.get_or_create(name=urldisplayname)
                obj.pattern = cPickle.dumps(prefixre + [u.regex])
                obj.save()

                self.stdout.write("%s: %s" % ("ADD" if bCreated else "UPDATE/KEEP", urldisplayname))

        traverse_urls(rooturl, patternFunc=_save_reg_api)

        for aep in (currAEP - newDiscovered):
            self.stdout.write("REMOVE: %s" % aep)
            APIEntryPoint.objects.get(name=aep).delete()


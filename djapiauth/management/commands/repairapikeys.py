# -*- coding: utf-8 -*-
import cPickle
from django.core.management.base import BaseCommand, CommandError
# from django.utils.module_loading import import_by_path
# from django.conf import settings

from ...models import APIKeys, APITree
# from ...utility import is_protected_api, traverse_urls

# rooturl = import_by_path(settings.ROOT_URLCONF+".urlpatterns")


class Command(BaseCommand):
    args = ''
    help = 'repair API key matching data'

    def handle(self, *args, **options):
        for ak in APIKeys.objects.all():
            tree = APITree()
            for api in ak.apis.all():
                srelist = cPickle.loads(api.pattern.encode("ascii"))
                tree.add(srelist)
            ak.apitree = cPickle.dumps(tree)
            ak.save(update_fields=["apitree"])
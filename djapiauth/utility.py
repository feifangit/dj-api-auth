import json
import datetime
import decimal
from django.http import HttpResponse
from django.core.urlresolvers import RegexURLResolver
from django.conf.urls import url
from django.core.urlresolvers import RegexURLPattern

from .auth import api_auth


def is_aware(value):
    """
    Determines if a given datetime.datetime is aware.

    The logic is described in Python's docs:
    http://docs.python.org/library/datetime.html#datetime.tzinfo
    """
    return value.tzinfo is not None and value.tzinfo.utcoffset(value) is not None


class DjangoJSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time and decimal types.
    """
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            if is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(DjangoJSONEncoder, self).default(o)


class JsonResponse(HttpResponse):
    """
    An HTTP response class that consumes data to be serialized to JSON.

    :param data: Data to be dumped into json. By default only ``dict`` objects
      are allowed to be passed due to a security flaw before EcmaScript 5. See
      the ``safe`` parameter for more information.
    :param encoder: Should be an json encoder class. Defaults to
      ``django.core.serializers.json.DjangoJSONEncoder``.
    :param safe: Controls if only ``dict`` objects may be serialized. Defaults
      to ``True``.
    """

    def __init__(self, data, encoder=DjangoJSONEncoder, safe=True, **kwargs):
        if safe and not isinstance(data, dict):
            raise TypeError('In order to allow non-dict objects to be '
                            'serialized set the safe parameter to False')
        kwargs.setdefault('content_type', 'application/json')
        data = json.dumps(data, cls=encoder)
        super(JsonResponse, self).__init__(content=data, **kwargs)


# neither reg_api nor reg_n_protect_api take effect on include(...)
def reg_api(regex, viewname, *args, **kwargs):  # api_auth added in view, make registration only
    urlobj = url(regex, viewname, *args, **kwargs)
    if isinstance(urlobj, RegexURLPattern):
        setattr(urlobj, "_protected_api", True)
    return urlobj


def reg_n_protect_api(regex, viewname, views, *args, **kwargs):
    """reuse an existing view, must provide views"""
    if not isinstance(viewname, (list, tuple)):  # not include
        urlobj = url(regex, api_auth(getattr(views, viewname)))
        setattr(urlobj, "_protected_api", True)
        return urlobj
    return url(regex, viewname, *args, **kwargs)  # ignore include


def is_protected_api(u):
    """ if a url is registered as protected """
    return hasattr(u, "_protected_api")


def traverse_urls(urlpattern, prefixre=[], prefixname=[], patternFunc=None, resolverFunc=None):
    """
    urlpattern: urlpattern object

    prefix?? : for multiple level urls defined in different urls.py files
    prefixre: compiled regex object
    prefixnames: regex text

    patternFunc: function to process RegexURLPattern
    resolverFunc: function to process RegexURLResolver
    """
    for u in urlpattern:
        if isinstance(u, RegexURLResolver):  # inspect sub urls
            if resolverFunc:
                resolverFunc(u, prefixre, prefixname)

            traverse_urls(u.url_patterns,
                          prefixre + [u.regex, ],
                          prefixname + [u._regex, ],
                          patternFunc,
                          resolverFunc)
        else:
            if patternFunc:
                patternFunc(u, prefixre, prefixname)

import json
import datetime
import decimal
from django.utils import six
from django.http import HttpResponse
from django.core.urlresolvers import RegexURLResolver
from django.conf.urls import url
from django.utils.module_loading import import_by_path
from django.views.decorators.csrf import csrf_exempt


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


def url_with_auth(regex, view, kwargs=None, name=None, prefix=''):
    """
    if view is string based, must be a full path
    """
    from djapiauth.auth import api_auth
    if isinstance(view, six.string_types):  # view is a string, must be full path
        return url(regex, api_auth(import_by_path(prefix + "." + view if prefix else view)))
    elif isinstance(view, (list, tuple)):  # include
        return url(regex, view, name, prefix, **kwargs)
    else:  # view is an object
        return url(regex, api_auth(view))


def is_protected_api(u):
    """ if a url is registered as protected """
    return u.callback and getattr(u.callback, "__djapiauth__", False)


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


class AuthMixin(object):
    """
    for class-based views
    derived classed can turn auth off by set api_auth to False
    """
    api_auth = True

    @classmethod
    def as_view(cls, **initkwargs):
        from djapiauth.auth import api_auth
        view = super(AuthMixin, cls).as_view(**initkwargs)
        view = api_auth(view) if cls.api_auth else view
        return csrf_exempt(view) if "post" in cls.http_method_names else view

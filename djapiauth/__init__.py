from django.conf import settings


default_app_config = 'djapiauth.apps.ApiAuthConfig'


def _load_setting(n, default):
    return getattr(settings, n) if hasattr(settings, n) else default

API_AUTH_ADMIN_USER_FILTER = _load_setting("API_AUTH_ADMIN_USER_FILTER", {})
API_AUTH_ALLOWED_TIME_DRIFT = _load_setting("API_AUTH_ALLOWED_TIME_DRIFT", 5*60)


__version__ = '0.7'
VERSION = tuple(map(int, __version__.split('.')))


# exposed functions and classes
try:
	from .utility import AuthMixin, url_with_auth
	from .auth import api_auth
except:
	pass
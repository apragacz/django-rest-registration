from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from rest_registration.settings import registration_settings


def get_login_authentication_backend() -> str:
    backends = settings.AUTHENTICATION_BACKENDS
    default_login_backend = registration_settings.LOGIN_DEFAULT_SESSION_AUTHENTICATION_BACKEND  # noqa: E501
    if not backends:
        raise ImproperlyConfigured("No AUTHENTICATION_BACKENDS specified")
    if len(backends) == 1:
        return backends[0]
    if default_login_backend not in backends:
        raise ImproperlyConfigured(
            "LOGIN_DEFAULT_SESSION_AUTHENTICATION_BACKEND"
            " is not in AUTHENTICATION_BACKENDS")
    return default_login_backend

import contextlib

from django.conf import settings
from django.test.utils import override_settings

from tests.helpers.common import shallow_merge_dicts


@contextlib.contextmanager
def override_rest_registration_settings(new_settings: dict = None):
    if new_settings is None:
        new_settings = {}
    with override_settings(
        REST_REGISTRATION=shallow_merge_dicts(
            settings.REST_REGISTRATION, new_settings),
    ):
        yield settings


@contextlib.contextmanager
def override_auth_model_settings(new_auth_model):
    with override_settings(AUTH_USER_MODEL=new_auth_model):
        yield settings

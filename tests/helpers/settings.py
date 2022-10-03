import contextlib
from typing import Callable

from django.conf import settings
from django.test.utils import TestContextDecorator, override_settings
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from tests.helpers.common import shallow_merge_dicts


def override_rest_registration_settings(new_settings: dict = None):
    if new_settings is None:
        new_settings = {}

    def processor(current_settings):
        return {
            'REST_REGISTRATION': shallow_merge_dicts(
                current_settings.REST_REGISTRATION, new_settings),
        }

    return OverrideSettingsDecorator(processor)


@contextlib.contextmanager
def override_rest_framework_settings_dict(settings_dict):
    try:
        with override_settings(REST_FRAMEWORK=settings_dict):
            _update_api_view_class_attrs()
            yield
    finally:
        _update_api_view_class_attrs()


def _update_api_view_class_attrs():
    attrs = [
        'renderer_classes', 'parser_classes', 'authentication_classes',
        'throttle_classes', 'permission_classes', 'content_negotiation_class',
        'metadata_class', 'versioning_class',
    ]
    for attr in attrs:
        attr_upper = attr.upper()
        api_settings_key = 'DEFAULT_{attr_upper}'.format(attr_upper=attr_upper)
        setattr(APIView, attr, getattr(api_settings, api_settings_key))


def override_auth_model_settings(new_auth_model):

    def processor(current_settings):
        return {'AUTH_USER_MODEL': new_auth_model}

    return OverrideSettingsDecorator(processor)


class OverrideSettingsDecorator(TestContextDecorator):

    def __init__(self, settings_processor: Callable[[dict], dict]):
        super().__init__()
        self._settings_processor = settings_processor
        # Parent decorator will be created on-demand.
        self._parent_decorator = None

    def enable(self):
        self._parent_decorator = self._build_parent_decorator()
        return self._parent_decorator.enable()

    def disable(self):
        try:
            return self._parent_decorator.disable()
        finally:
            self._parent_decorator = None

    def decorate_class(self, cls):
        return self._build_parent_decorator().decorate_class(cls)

    def _build_parent_decorator(self) -> TestContextDecorator:
        updated_settings = self._settings_processor(settings)
        return override_settings(**updated_settings)

from typing import Callable

from django.conf import settings
from django.test.utils import TestContextDecorator, override_settings

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


def override_auth_model_settings(new_auth_model):

    def processor(current_settings):
        return {'AUTH_USER_MODEL': new_auth_model}

    return OverrideSettingsDecorator(processor)


class OverrideSettingsDecorator(TestContextDecorator):

    def __init__(self, settings_processor: Callable[[dict], dict]):
        super().__init__()
        self._settings_processor = settings_processor
        # Parent decorator will be created lazily.
        self._parent_decorator = None

    def enable(self):
        self._reset_parent_decorator()
        return self.parent_decorator.enable()

    def disable(self):
        try:
            return self.parent_decorator.disable()
        finally:
            self._reset_parent_decorator()

    def decorate_class(self, cls):
        self._reset_parent_decorator()
        try:
            return self.parent_decorator.decorate_class(cls)
        finally:
            self._reset_parent_decorator()

    def _reset_parent_decorator(self):
        self._parent_decorator = None

    @property
    def parent_decorator(self) -> TestContextDecorator:
        if self._parent_decorator is None:
            updated_settings = self._settings_processor(settings)
            self._parent_decorator = override_settings(**updated_settings)
        return self._parent_decorator

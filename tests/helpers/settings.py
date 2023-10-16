from typing import Any, Callable, Dict, Optional

from django.conf import LazySettings, settings
from django.test.utils import TestContextDecorator, override_settings
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from tests.helpers.common import shallow_merge_dicts

_API_VIEW_FIELDS = [
    "renderer_classes",
    "parser_classes",
    "authentication_classes",
    "throttle_classes",
    "permission_classes",
    "content_negotiation_class",
    "metadata_class",
    "versioning_class",
]


def _noop():
    pass


def _api_view_fields_patcher():
    for field_name in _API_VIEW_FIELDS:
        api_settings_name = f"DEFAULT_{field_name.upper()}"
        api_setting_value = getattr(api_settings, api_settings_name)
        setattr(APIView, field_name, api_setting_value)


def override_rest_registration_settings(
    new_settings: Optional[Dict[str, Any]] = None,
) -> TestContextDecorator:
    if new_settings is None:
        new_settings = {}

    def processor(current_settings: LazySettings) -> Dict[str, Any]:
        return {
            'REST_REGISTRATION': shallow_merge_dicts(
                current_settings.REST_REGISTRATION, new_settings),
        }

    return OverrideSettingsDecorator(processor, _noop)


def override_rest_framework_settings(
    new_settings: Optional[Dict[str, Any]] = None,
) -> TestContextDecorator:
    if new_settings is None:
        new_settings = {}

    def processor(current_settings: LazySettings) -> Dict[str, Any]:
        current_rest_framework_settings = getattr(
            current_settings, "REST_FRAMEWORK", {},
        )
        return {
            "REST_FRAMEWORK": shallow_merge_dicts(
                current_rest_framework_settings, new_settings),
        }

    return OverrideSettingsDecorator(processor, _api_view_fields_patcher)


def override_auth_model_settings(new_auth_model):

    def processor(current_settings):
        return {'AUTH_USER_MODEL': new_auth_model}

    return OverrideSettingsDecorator(processor, _noop)


class OverrideSettingsDecorator(TestContextDecorator):

    def __init__(
        self,
        settings_processor: Callable[[LazySettings], Dict[str, Any]],
        patcher: Callable[[], None],
    ) -> None:
        super().__init__()
        self._settings_processor = settings_processor
        self._patcher = patcher
        # Parent decorator will be created on-demand.
        self._parent_decorator = None

    def enable(self):
        self._parent_decorator = self._build_parent_decorator()
        self._parent_decorator.enable()
        self._patcher()

    def disable(self):
        try:
            return self._parent_decorator.disable()
        finally:
            self._parent_decorator = None
            self._patcher()

    def decorate_class(self, cls):
        return self._build_parent_decorator().decorate_class(cls)

    def _build_parent_decorator(self) -> TestContextDecorator:
        updated_settings = self._settings_processor(settings)
        return override_settings(**updated_settings)

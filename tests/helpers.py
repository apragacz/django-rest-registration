import contextlib

from django.test.utils import override_settings
from rest_framework.settings import api_settings
from rest_framework.views import APIView


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

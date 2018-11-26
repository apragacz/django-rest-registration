from django.test.signals import setting_changed

from rest_registration.settings_fields import SETTINGS_FIELDS
from rest_registration.utils.nested_settings import NestedSettings

DEFAULTS = {f.name: f.default for f in SETTINGS_FIELDS}
IMPORT_STRINGS = [f.name for f in SETTINGS_FIELDS if f.import_string]


registration_settings = NestedSettings(
    None, DEFAULTS, IMPORT_STRINGS,
    root_setting_name='REST_REGISTRATION')


def settings_changed_handler(*args, **kwargs):
    registration_settings.reset_user_settings()
    registration_settings.reset_attr_cache()


setting_changed.connect(settings_changed_handler)

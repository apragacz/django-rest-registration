from django.test.signals import setting_changed

from rest_registration.utils.nested_settings import NestedSettings

DEFAULTS = {
    'VERIFY_REGISTRATION_SUCCESS_URL': None,
    'VERIFY_REGISTRATION_FAILURE_URL': None,

    'VERIFY_EMAIL_SUCCESS_URL': None,
    'VERIFY_EMAIL_FAILURE_URL': None,

    'RESET_PASSWORD_SUCCESS_URL': None,
    'RESET_PASSWORD_FAILURE_URL': None,
}

IMPORT_STRINGS = ()

verification_redirects_settings = NestedSettings(
    None, DEFAULTS, IMPORT_STRINGS,
    root_setting_name='REST_REGISTRATION_VERIFICATION_REDIRECTS')


def settings_changed_handler(*args, **kwargs) -> None:
    verification_redirects_settings.reset_user_settings()
    verification_redirects_settings.reset_attr_cache()


setting_changed.connect(settings_changed_handler)

import datetime

from django.conf import settings as root_settings
from django.test.signals import setting_changed
from rest_framework.settings import perform_import

DEFAULTS = {
    'USER_LOGIN_FIELDS': None,
    'USER_HIDDEN_FIELDS': (
        'is_active',
        'is_staff',
        'is_superuser',
        'user_permissions',
        'groups',
        'date_joined',
    ),
    'USER_PUBLIC_FIELDS': None,
    'USER_EDITABLE_FIELDS': None,
    'USER_EMAIL_FIELD': 'email',

    'USER_VERIFICATION_FLAG_FIELD': 'is_active',

    'REGISTER_SERIALIZER_CLASS': 'rest_registration.api.serializers.DefaultRegisterUserSerializer',  # noqa: E501
    'REGISTER_SERIALIZER_PASSWORD_CONFIRM': True,

    'REGISTER_OUTPUT_SERIALIZER_CLASS': 'rest_registration.api.serializers.DefaultUserProfileSerializer',  # noqa: E501

    'REGISTER_VERIFICATION_ENABLED': True,
    'REGISTER_VERIFICATION_PERIOD': datetime.timedelta(days=7),
    'REGISTER_VERIFICATION_URL': None,
    'REGISTER_VERIFICATION_EMAIL_TEMPLATES': {
        'subject':  'rest_registration/register/subject.txt',
        'body':  'rest_registration/register/body.txt',
    },

    'LOGIN_SERIALIZER_CLASS': 'rest_registration.api.serializers.DefaultLoginSerializer',  # noqa: E501
    'LOGIN_AUTHENTICATE_SESSION': None,
    'LOGIN_RETRIEVE_TOKEN': None,

    'RESET_PASSWORD_VERIFICATION_PERIOD': datetime.timedelta(days=1),
    'RESET_PASSWORD_VERIFICATION_URL': None,
    'RESET_PASSWORD_VERIFICATION_EMAIL_TEMPLATES': {
        'subject': 'rest_registration/reset_password/subject.txt',
        'body': 'rest_registration/reset_password/body.txt',
    },

    'REGISTER_EMAIL_VERIFICATION_ENABLED': True,
    'REGISTER_EMAIL_VERIFICATION_PERIOD': datetime.timedelta(days=7),
    'REGISTER_EMAIL_VERIFICATION_URL': None,
    'REGISTER_EMAIL_VERIFICATION_EMAIL_TEMPLATES': {
        'subject':  'rest_registration/register_email/subject.txt',
        'body':  'rest_registration/register_email/body.txt',
    },

    'PROFILE_SERIALIZER_CLASS': 'rest_registration.api.serializers.DefaultUserProfileSerializer',  # noqa: E501

    'VERIFICATION_FROM_EMAIL': None,
    'VERIFICATION_REPLY_TO_EMAIL': None,
    'VERIFICATION_EMAIL_HTML_TO_TEXT_CONVERTER': 'rest_registration.utils.convert_html_to_text_preserving_urls',  # noqa: E501

    'SUCCESS_RESPONSE_BUILDER': 'rest_registration.utils.build_default_success_response',  # noqa: E501
}

IMPORT_STRINGS = (
    'REGISTER_SERIALIZER_CLASS',
    'REGISTER_OUTPUT_SERIALIZER_CLASS',
    'LOGIN_SERIALIZER_CLASS',
    'PROFILE_SERIALIZER_CLASS',
    'VERIFICATION_EMAIL_HTML_TO_TEXT_CONVERTER',
    'SUCCESS_RESPONSE_BUILDER',
)


class NestedSettings(object):
    def __init__(
            self, user_settings, defaults, import_strings,
            root_setting_name):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults
        self.import_strings = import_strings
        self.root_setting_name = root_setting_name

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(
                root_settings,
                self.root_setting_name,
                {},
            )
        return self._user_settings

    def reset_user_settings(self):
        if hasattr(self, '_user_settings'):
            del self._user_settings

    def reset_attr_cache(self):
        for key in self.defaults.keys():
            if hasattr(self, key):
                delattr(self, key)

    def __getattr__(self, attr):
        if attr not in self.defaults.keys():
            raise AttributeError(
                "Invalid {self.root_setting_name} setting: '{attr}'".format(
                    self=self, attr=attr))

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        setattr(self, attr, val)
        return val


registration_settings = NestedSettings(
    None, DEFAULTS, IMPORT_STRINGS,
    root_setting_name='REST_REGISTRATION')


def settings_changed_handler(*args, **kwargs):
    registration_settings.reset_user_settings()
    registration_settings.reset_attr_cache()


setting_changed.connect(settings_changed_handler)

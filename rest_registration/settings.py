from django.conf import settings
from rest_framework.settings import perform_import


DEFAULTS = {
    'USER_LOGIN_FIELDS': None,
    'USER_HIDDEN_FIELDS': (),
    'USER_PUBLIC_FIELDS': None,
}

IMPORT_STRINGS = (
)


class RegistrationSettings(object):
    def __init__(self, user_settings, defaults, import_strings):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults
        self.import_strings = import_strings

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'REST_REGISTRATION', {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults.keys():
            raise AttributeError("Invalid registration setting: '%s'" % attr)

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


settings = RegistrationSettings(None, DEFAULTS, IMPORT_STRINGS)  # noqa

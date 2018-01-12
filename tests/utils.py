from . import default_settings
from django.conf import settings


def configure_settings():
    settings_dict = {
        key: value for key, value in vars(default_settings).items()
        if not key.startswith('_') and key.upper() == key
    }
    settings.configure(**settings_dict)

from django.conf import settings
from django.core.checks import register
from django.core.exceptions import ImproperlyConfigured
from rest_framework.authentication import TokenAuthentication
from rest_framework.settings import api_settings

from rest_registration.decorators import simple_check
from rest_registration.notifications.email import parse_template_config
from rest_registration.settings import registration_settings


class ErrorCode:  # pylint: disable=too-few-public-methods
    NO_RESET_PASSWORD_VER_URL = 'E001'
    NO_REGISTER_VER_URL = 'E002'
    NO_REGISTER_EMAIL_VER_URL = 'E003'
    NO_VER_FROM_EMAIL = 'E004'
    NO_TOKEN_AUTH_CONFIG = 'E005'
    NO_TOKEN_AUTH_INSTALLED = 'E006'
    INVALID_EMAIL_TEMPLATE_CONFIG = 'E007'
    NO_AUTH_INSTALLED = 'E008'
    DRF_INCOMPATIBLE_DJANGO_AUTH_BACKEND = 'E009'


class WarningCode:  # pylint: disable=too-few-public-methods
    REGISTER_VERIFICATION_MULTIPLE_AUTO_LOGIN = 'W001'


@register()
@simple_check(
    'django.contrib.auth is not in INSTALLED_APPS',
    ErrorCode.NO_AUTH_INSTALLED,
)
def auth_installed_check():
    return 'django.contrib.auth' in settings.INSTALLED_APPS


@register()
@simple_check(
    'RESET_PASSWORD_VERIFICATION_URL is not set',
    ErrorCode.NO_RESET_PASSWORD_VER_URL,
)
def reset_password_verification_url_check():
    return implies(
        registration_settings.RESET_PASSWORD_VERIFICATION_ENABLED,
        registration_settings.RESET_PASSWORD_VERIFICATION_URL,
    )


@register()
@simple_check(
    'register verification is enabled,'
    ' but REGISTER_VERIFICATION_URL is not set',
    ErrorCode.NO_REGISTER_VER_URL,
)
def register_verification_url_check():
    return implies(
        registration_settings.REGISTER_VERIFICATION_ENABLED,
        registration_settings.REGISTER_VERIFICATION_URL,
    )


@register()
@simple_check(
    'register email verification is enabled,'
    ' but REGISTER_EMAIL_VERIFICATION_URL is not set',
    ErrorCode.NO_REGISTER_EMAIL_VER_URL,
)
def register_email_verification_url_check():
    return implies(
        registration_settings.REGISTER_EMAIL_VERIFICATION_ENABLED,
        registration_settings.REGISTER_EMAIL_VERIFICATION_URL,
    )


@register()
@simple_check(
    'VERIFICATION_FROM_EMAIL is not set',
    ErrorCode.NO_VER_FROM_EMAIL,
)
def verification_from_check():
    return implies(
        any([
            registration_settings.REGISTER_VERIFICATION_ENABLED,
            registration_settings.REGISTER_EMAIL_VERIFICATION_ENABLED,
            registration_settings.RESET_PASSWORD_VERIFICATION_ENABLED,
        ]),
        registration_settings.VERIFICATION_FROM_EMAIL,
    )


@register()
@simple_check(
    'LOGIN_RETRIEVE_TOKEN is set but'
    ' TokenAuthentication is not in DEFAULT_AUTHENTICATION_CLASSES',
    ErrorCode.NO_TOKEN_AUTH_CONFIG,
)
def token_auth_config_check():
    return implies(
        registration_settings.LOGIN_RETRIEVE_TOKEN,
        any(
            issubclass(cls, TokenAuthentication)
            for cls in api_settings.DEFAULT_AUTHENTICATION_CLASSES
        )
    )


@register()
@simple_check(
    'LOGIN_RETRIEVE_TOKEN is set but'
    ' rest_framework.authtoken is not in INSTALLED_APPS',
    ErrorCode.NO_TOKEN_AUTH_INSTALLED,
)
def token_auth_installed_check():
    return implies(
        registration_settings.LOGIN_RETRIEVE_TOKEN,
        'rest_framework.authtoken' in settings.INSTALLED_APPS,
    )


@register()
@simple_check(
    'REGISTER_VERIFICATION_AUTO_LOGIN is enabled,'
    ' but REGISTER_VERIFICATION_ONE_TIME_USE is not enabled.'
    ' This can allow multiple logins using the verification url.',
    WarningCode.REGISTER_VERIFICATION_MULTIPLE_AUTO_LOGIN,
)
def register_verification_one_time_auto_login_check():
    return implies(
        all([
            registration_settings.REGISTER_VERIFICATION_ENABLED,
            registration_settings.REGISTER_VERIFICATION_AUTO_LOGIN,
        ]),
        registration_settings.REGISTER_VERIFICATION_ONE_TIME_USE,
    )


@register()
@simple_check(
    'REGISTER_VERIFICATION_EMAIL_TEMPLATES is invalid',
    ErrorCode.INVALID_EMAIL_TEMPLATE_CONFIG,
)
def valid_register_verification_email_template_config_check():
    return _is_email_template_config_valid(
        registration_settings.REGISTER_VERIFICATION_EMAIL_TEMPLATES)


@register()
@simple_check(
    'RESET_PASSWORD_VERIFICATION_EMAIL_TEMPLATES is invalid',
    ErrorCode.INVALID_EMAIL_TEMPLATE_CONFIG,
)
def valid_reset_password_verification_email_template_config_check():
    return _is_email_template_config_valid(
        registration_settings.RESET_PASSWORD_VERIFICATION_EMAIL_TEMPLATES)


@register()
@simple_check(
    'REGISTER_EMAIL_VERIFICATION_EMAIL_TEMPLATES is invalid',
    ErrorCode.INVALID_EMAIL_TEMPLATE_CONFIG,
)
def valid_register_email_verification_email_template_config_check():
    return _is_email_template_config_valid(
        registration_settings.REGISTER_EMAIL_VERIFICATION_EMAIL_TEMPLATES)


def _is_email_template_config_valid(template_config_data):
    try:
        parse_template_config(template_config_data)
    except ImproperlyConfigured:
        return False
    else:
        return True


# The backends below allow inactive users to autenticate, which makes them
# incompatible with Django REST Framework authentication classes
# which check whether the is_active flag is set before authenticating.
#
# See https://github.com/apragacz/django-rest-registration/issues/52
#
__DRF_INCOMPATIBLE_DJANGO_AUTH_BACKENDS__ = [
    'django.contrib.auth.backends.AllowAllUsersModelBackend',
    'django.contrib.auth.backends.AllowAllUsersRemoteUserBackend',
]


@register()
@simple_check(
    'One of following Django authentication backends (which are incompatible'
    ' with Django REST Framework authentication classes) is being used:\n\n'
    + '\n'.join(__DRF_INCOMPATIBLE_DJANGO_AUTH_BACKENDS__),
    ErrorCode.DRF_INCOMPATIBLE_DJANGO_AUTH_BACKEND,
)
def drf_compatible_django_auth_backend_check():
    return all(
        incompat_cls_name not in settings.AUTHENTICATION_BACKENDS
        for incompat_cls_name in __DRF_INCOMPATIBLE_DJANGO_AUTH_BACKENDS__
    )


def implies(premise, conclusion):
    return not premise or conclusion


__ALL_CHECKS__ = [
    auth_installed_check,
    reset_password_verification_url_check,
    register_verification_url_check,
    register_email_verification_url_check,
    verification_from_check,
    token_auth_config_check,
    token_auth_installed_check,
    register_verification_one_time_auto_login_check,
    valid_register_verification_email_template_config_check,
    valid_reset_password_verification_email_template_config_check,
    valid_register_email_verification_email_template_config_check,
    drf_compatible_django_auth_backend_check,
]

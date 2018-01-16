from django.conf import settings
from django.core.checks import register
from rest_framework.authentication import TokenAuthentication
from rest_framework.settings import api_settings

from rest_registration.decorators import simple_check
from rest_registration.settings import registration_settings


class ErrorCode(object):
    NO_RESET_PASSWORD_VER_URL = 'E001'
    NO_REGISTER_VER_URL = 'E002'
    NO_REGISTER_EMAIL_VER_URL = 'E003'
    NO_VER_FROM_EMAIL = 'E004'
    NO_TOKEN_AUTH_CONFIG = 'E005'
    NO_TOKEN_AUTH_INSTALLED = 'E006'


@register()
@simple_check(
    'RESET_PASSWORD_VERIFICATION_URL is not set',
    ErrorCode.NO_RESET_PASSWORD_VER_URL,
)
def reset_password_verification_url_check():
    return registration_settings.RESET_PASSWORD_VERIFICATION_URL


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
    return registration_settings.VERIFICATION_FROM_EMAIL


@register()
@simple_check(
    'LOGIN_RETRIEVE_TOKEN is set but'
    ' TokenAuthentication is not in DEFAULT_AUTHENTICATION_CLASSES',
    ErrorCode.NO_TOKEN_AUTH_CONFIG,
)
def token_auth_config_check():
    return implies(
        registration_settings.LOGIN_RETRIEVE_TOKEN,
        TokenAuthentication in api_settings.DEFAULT_AUTHENTICATION_CLASSES,
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


def implies(premise, conclusion):
    return not premise or conclusion


__ALL_CHECKS__ = [
    reset_password_verification_url_check,
    register_verification_url_check,
    register_email_verification_url_check,
    verification_from_check,
    token_auth_config_check,
    token_auth_installed_check,
]

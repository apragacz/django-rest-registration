from django.core.checks import register

from rest_registration.decorators import simple_check
from rest_registration.settings import registration_settings


class ErrorCode(object):
    NO_RESET_PASSWORD_VER_URL = 'E001'
    NO_REGISTER_VER_URL = 'E002'
    NO_REGISTER_EMAIL_VER_URL = 'E003'
    NO_VER_FROM_EMAIL = 'E004'


@register()
@simple_check('RESET_PASSWORD_VERIFICATION_URL is not set',
              ErrorCode.NO_RESET_PASSWORD_VER_URL)
def reset_password_verification_url_check():
    return registration_settings.RESET_PASSWORD_VERIFICATION_URL


@register()
@simple_check('register verification is enabled,'
              ' but REGISTER_VERIFICATION_URL is not set',
              ErrorCode.NO_REGISTER_VER_URL)
def register_verification_url_check():
    return (not registration_settings.REGISTER_VERIFICATION_ENABLED or
            registration_settings.REGISTER_VERIFICATION_URL)


@register()
@simple_check('register email verification is enabled,'
              ' but REGISTER_EMAIL_VERIFICATION_URL is not set',
              ErrorCode.NO_REGISTER_EMAIL_VER_URL)
def register_email_verification_url_check():
    return (not registration_settings.REGISTER_EMAIL_VERIFICATION_ENABLED or
            registration_settings.REGISTER_EMAIL_VERIFICATION_URL)


@register()
@simple_check('VERIFICATION_FROM_EMAIL is not set',
              ErrorCode.NO_VER_FROM_EMAIL)
def verification_from_check():
    return registration_settings.VERIFICATION_FROM_EMAIL


__ALL_CHECKS__ = [
    reset_password_verification_url_check,
    register_verification_url_check,
    register_email_verification_url_check,
    verification_from_check,
]

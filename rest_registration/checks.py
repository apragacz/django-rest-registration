from django.core.checks import Error, register

from rest_registration.settings import registration_settings


@register()
def reset_password_verification_url_check(app_configs, **kwargs):
    errors = []
    if not registration_settings.RESET_PASSWORD_VERIFICATION_URL:
        errors.append(
            Error(
                ' RESET_PASSWORD_VERIFICATION_URL is not set',
                hint=None,
                obj=registration_settings,
                id='rest_registration.E001',
            )
        )
    return errors


@register()
def register_verification_url_check(app_configs, **kwargs):
    errors = []
    if (registration_settings.REGISTER_VERIFICATION_ENABLED and
            not registration_settings.REGISTER_VERIFICATION_URL):
        errors.append(
            Error(
                'register verification is enabled,'
                ' but REGISTER_VERIFICATION_URL is not set',
                hint=None,
                obj=registration_settings,
                id='rest_registration.E002',
            )
        )
    return errors


@register()
def register_email_verification_url_check(app_configs, **kwargs):
    errors = []
    if (registration_settings.REGISTER_EMAIL_VERIFICATION_ENABLED and
            not registration_settings.REGISTER_EMAIL_VERIFICATION_URL):
        errors.append(
            Error(
                'register email verification is enabled,'
                ' but REGISTER_EMAIL_VERIFICATION_URL is not set',
                hint=None,
                obj=registration_settings,
                id='rest_registration.E003',
            )
        )
    return errors


@register()
def reset_password_verification_url_check(app_configs, **kwargs):
    errors = []
    if not registration_settings.VERIFICATION_FROM_EMAIL:
        errors.append(
            Error(
                ' VERIFICATION_FROM_EMAIL is not set',
                hint=None,
                obj=registration_settings,
                id='rest_registration.E004',
            )
        )
    return errors

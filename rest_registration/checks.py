from django.core.checks import Error, register

from rest_registration.settings import registration_settings


def check(message, error_code):

    def decorator(predicate):

        def f(app_configs, **kwargs):
            errors = []
            if not predicate():
                errors.append(
                    Error(
                        message,
                        hint=None,
                        id='rest_registration.E{0}'.format(error_code),
                    )
                )
            return errors

        return f

    return decorator


@register()
@check('RESET_PASSWORD_VERIFICATION_URL is not set', '001')
def reset_password_verification_url_check():
    return registration_settings.RESET_PASSWORD_VERIFICATION_URL


@register()
@check('register verification is enabled,'
       ' but REGISTER_VERIFICATION_URL is not set', '002')
def register_verification_url_check():
    return (not registration_settings.REGISTER_VERIFICATION_ENABLED or
            registration_settings.REGISTER_VERIFICATION_URL)


@register()
@check('register email verification is enabled,'
       ' but REGISTER_EMAIL_VERIFICATION_URL is not set', '003')
def register_email_verification_url_check():
    return (not registration_settings.REGISTER_EMAIL_VERIFICATION_ENABLED or
            registration_settings.REGISTER_EMAIL_VERIFICATION_URL)


@register()
@check('VERIFICATION_FROM_EMAIL is not set', '004')
def verification_from_check():
    return registration_settings.VERIFICATION_FROM_EMAIL

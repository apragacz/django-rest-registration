from functools import partial
from typing import Type

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.checks import register
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model
from rest_framework.settings import api_settings

from rest_registration.auth_token_managers import AbstractAuthTokenManager
from rest_registration.enums import ErrorCode, WarningCode
from rest_registration.settings import registration_settings
from rest_registration.utils.auth_backends import get_login_authentication_backend
from rest_registration.utils.checks import no_exception_check, predicate_check
from rest_registration.utils.common import implies
from rest_registration.utils.email import parse_template_config
from rest_registration.utils.users import (
    get_user_email_field_name,
    get_user_login_field_names,
    is_model_field_unique
)


@register()
@predicate_check(
    'django.contrib.auth is not in INSTALLED_APPS',
    ErrorCode.NO_AUTH_INSTALLED,
)
def auth_installed_check() -> bool:
    return _is_auth_installed()


@register()
@predicate_check(
    'RESET_PASSWORD_VERIFICATION_URL is not set',
    ErrorCode.NO_RESET_PASSWORD_VER_URL,
)
def reset_password_verification_url_check() -> bool:
    sends_emails = (registration_settings.RESET_PASSWORD_VERIFICATION_ENABLED
                    and registration_settings.is_default(
                        'RESET_PASSWORD_VERIFICATION_EMAIL_SENDER'))
    return implies(
        sends_emails,
        registration_settings.RESET_PASSWORD_VERIFICATION_URL,
    )


@register()
@predicate_check(
    'register verification is enabled,'
    ' but REGISTER_VERIFICATION_URL is not set',
    ErrorCode.NO_REGISTER_VER_URL,
)
def register_verification_url_check() -> bool:
    sends_emails = (registration_settings.REGISTER_VERIFICATION_ENABLED
                    and registration_settings.is_default(
                        'REGISTER_VERIFICATION_EMAIL_SENDER'))
    return implies(
        sends_emails,
        registration_settings.REGISTER_VERIFICATION_URL,
    )


@register()
@predicate_check(
    'register email verification is enabled,'
    ' but REGISTER_EMAIL_VERIFICATION_URL is not set',
    ErrorCode.NO_REGISTER_EMAIL_VER_URL,
)
def register_email_verification_url_check() -> bool:
    sends_emails = (registration_settings.REGISTER_EMAIL_VERIFICATION_ENABLED
                    and registration_settings.is_default(
                        'REGISTER_EMAIL_VERIFICATION_EMAIL_SENDER'))
    return implies(
        sends_emails,
        registration_settings.REGISTER_EMAIL_VERIFICATION_URL,
    )


@register()
@predicate_check(
    'VERIFICATION_FROM_EMAIL is not set',
    ErrorCode.NO_VER_FROM_EMAIL,
)
def verification_from_check() -> bool:
    sends_emails = any([
        registration_settings.REGISTER_VERIFICATION_ENABLED
        and registration_settings.is_default(
            'REGISTER_VERIFICATION_EMAIL_SENDER'),
        registration_settings.REGISTER_EMAIL_VERIFICATION_ENABLED
        and registration_settings.is_default(
            'REGISTER_EMAIL_VERIFICATION_EMAIL_SENDER'),
        registration_settings.RESET_PASSWORD_VERIFICATION_ENABLED
        and registration_settings.is_default(
            'RESET_PASSWORD_VERIFICATION_EMAIL_SENDER'),
    ])
    return implies(
        sends_emails,
        registration_settings.VERIFICATION_FROM_EMAIL,
    )


@register()
@predicate_check(
    'LOGIN_RETRIEVE_TOKEN is set but'
    ' the matching token authentication class is not'
    ' in DEFAULT_AUTHENTICATION_CLASSES',
    ErrorCode.NO_TOKEN_AUTH_CONFIG,
)
def token_auth_config_check() -> bool:
    return implies(
        _is_auth_installed() and registration_settings.LOGIN_RETRIEVE_TOKEN,
        _is_auth_token_manager_auth_class_enabled
    )


@register()
@predicate_check(
    'LOGIN_RETRIEVE_TOKEN is set but'
    ' the required Django apps are not in INSTALLED_APPS',
    ErrorCode.NO_TOKEN_AUTH_INSTALLED,
)
def token_auth_installed_check() -> bool:
    return implies(
        _is_auth_installed() and registration_settings.LOGIN_RETRIEVE_TOKEN,
        _is_auth_token_manager_app_name_installed,
    )


def _is_auth_token_manager_auth_class_enabled() -> bool:
    auth_token_manager = _get_auth_token_manager()
    auth_cls = auth_token_manager.get_authentication_class()
    return any(
        issubclass(cls, auth_cls)
        for cls in api_settings.DEFAULT_AUTHENTICATION_CLASSES
    )


def _is_auth_token_manager_app_name_installed() -> bool:
    auth_token_manager = _get_auth_token_manager()
    app_names = auth_token_manager.get_app_names()
    return all(app_name in settings.INSTALLED_APPS for app_name in app_names)


def _get_auth_token_manager() -> AbstractAuthTokenManager:
    auth_token_manager_cls = registration_settings.AUTH_TOKEN_MANAGER_CLASS
    auth_token_manager = auth_token_manager_cls()
    return auth_token_manager


@register()
@predicate_check(
    'REGISTER_VERIFICATION_AUTO_LOGIN is enabled,'
    ' but REGISTER_VERIFICATION_ONE_TIME_USE is not enabled.'
    ' This can allow multiple logins using the verification url.',
    WarningCode.REGISTER_VERIFICATION_MULTIPLE_AUTO_LOGIN,
)
def register_verification_one_time_auto_login_check() -> bool:
    return implies(
        all([
            registration_settings.REGISTER_VERIFICATION_ENABLED,
            registration_settings.REGISTER_VERIFICATION_AUTO_LOGIN,
        ]),
        registration_settings.REGISTER_VERIFICATION_ONE_TIME_USE,
    )


@register()
@no_exception_check(
    'REGISTER_VERIFICATION_EMAIL_TEMPLATES is invalid',
    ErrorCode.INVALID_EMAIL_TEMPLATE_CONFIG,
)
def valid_register_verification_email_template_config_check() -> None:
    sends_emails = (registration_settings.REGISTER_VERIFICATION_ENABLED
                    and registration_settings.is_default(
                        'REGISTER_VERIFICATION_EMAIL_SENDER'))
    _validate_email_template_config(
        sends_emails,
        registration_settings.REGISTER_VERIFICATION_EMAIL_TEMPLATES,
    )


@register()
@no_exception_check(
    'RESET_PASSWORD_VERIFICATION_EMAIL_TEMPLATES is invalid',
    ErrorCode.INVALID_EMAIL_TEMPLATE_CONFIG,
)
def valid_reset_password_verification_email_template_config_check() -> None:
    sends_emails = (registration_settings.RESET_PASSWORD_VERIFICATION_ENABLED
                    and registration_settings.is_default(
                        'RESET_PASSWORD_VERIFICATION_EMAIL_SENDER'))
    _validate_email_template_config(
        sends_emails,
        registration_settings.RESET_PASSWORD_VERIFICATION_EMAIL_TEMPLATES,
    )


@register()
@no_exception_check(
    'REGISTER_EMAIL_VERIFICATION_EMAIL_TEMPLATES is invalid',
    ErrorCode.INVALID_EMAIL_TEMPLATE_CONFIG,
)
def valid_register_email_verification_email_template_config_check() -> None:
    sends_emails = (registration_settings.REGISTER_EMAIL_VERIFICATION_ENABLED
                    and registration_settings.is_default(
                        'REGISTER_EMAIL_VERIFICATION_EMAIL_SENDER'))
    _validate_email_template_config(
        sends_emails,
        registration_settings.REGISTER_EMAIL_VERIFICATION_EMAIL_TEMPLATES,
    )


def _is_email_template_config_valid(template_config_data) -> bool:
    try:
        parse_template_config(template_config_data)
    except ImproperlyConfigured:
        return False
    else:
        return True


def _validate_email_template_config(enabled, template_config_data) -> None:
    if not enabled:
        return
    parse_template_config(template_config_data)


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
@predicate_check(
    'One of following Django authentication backends (which are incompatible'
    ' with Django REST Framework authentication classes) is being used:\n\n'
    + '\n'.join(__DRF_INCOMPATIBLE_DJANGO_AUTH_BACKENDS__),
    ErrorCode.DRF_INCOMPATIBLE_DJANGO_AUTH_BACKEND,
)
def drf_compatible_django_auth_backend_check() -> bool:
    return all(
        incompat_cls_name not in settings.AUTHENTICATION_BACKENDS
        for incompat_cls_name in __DRF_INCOMPATIBLE_DJANGO_AUTH_BACKENDS__
    )


@register()
@predicate_check(
    'At least one of LOGIN_FIELDS is not unique',
    ErrorCode.LOGIN_FIELDS_NOT_UNIQUE,
)
def login_fields_unique_check() -> bool:
    return implies(_is_auth_installed(), _are_login_fields_unique)


def _are_login_fields_unique() -> bool:
    user_cls = get_user_model()  # type: Type[Model]
    user_meta = user_cls._meta  # pylint: disable=protected-access
    return all(
        is_model_field_unique(user_meta.get_field(field_name))
        for field_name in get_user_login_field_names())


@register()
@predicate_check(
    'AUTH_TOKEN_MANAGER_CLASS is not proper subclass'
    ' of AbstractAuthTokenManager',
    ErrorCode.INVALID_AUTH_TOKEN_MANAGER_CLASS,
)
def valid_auth_token_manager_class_proper_subclass_check() -> bool:
    return implies(
        _is_auth_installed(),
        _is_auth_token_manager_proper_subclass,
    )


@register()
@predicate_check(
    'AUTH_TOKEN_MANAGER_CLASS is not implementing'
    ' method get_authentication_class',
    ErrorCode.INVALID_AUTH_TOKEN_MANAGER_CLASS,
)
def valid_auth_token_manager_class_get_authentication_class_check() -> bool:
    return implies(
        _is_auth_installed(),
        partial(
            _is_auth_token_manager_class_implementing_method,
            'get_authentication_class'),
    )


@register()
@predicate_check(
    'AUTH_TOKEN_MANAGER_CLASS is not implementing method provide_token',
    ErrorCode.INVALID_AUTH_TOKEN_MANAGER_CLASS,
)
def valid_auth_token_manager_class_provide_token_check() -> bool:
    return implies(
        _is_auth_installed(),
        partial(
            _is_auth_token_manager_class_implementing_method,
            'provide_token'),
    )


@register()
@no_exception_check(
    'invalid authentication backends configuration',
    ErrorCode.INVALID_AUTH_BACKENDS_CONFIG,
)
def valid_login_authentication_backend_check() -> None:
    get_login_authentication_backend()


# TODO: Issue #114 - remove deprecation check
@register()
@predicate_check(
    'LOGIN_SERIALIZER_CLASS contains deprecated get_authenticated_user method,'
    ' which will be removed in version 0.7.0;'
    ' for a replacement, please refer to LOGIN_AUTHENTICATOR setting',
    WarningCode.DEPRECATION
)
def deprecated_login_serializer_check() -> bool:
    serializer_class = registration_settings.LOGIN_SERIALIZER_CLASS
    deprecated = (
        hasattr(serializer_class, 'get_authenticated_user')
        and callable(serializer_class.get_authenticated_user))
    return not deprecated


# TODO: Issue #114 - remove deprecation check
@register()
@predicate_check(
    'SEND_RESET_PASSWORD_LINK_SERIALIZER_CLASS contains deprecated'
    ' get_user_or_none method, which will be removed in version 0.7.0;'
    ' for a replacement, please refer to SEND_RESET_PASSWORD_LINK_USER_FINDER setting',
    WarningCode.DEPRECATION
)
def deprecated_send_reset_password_link_serializer_check() -> bool:
    serializer_class = registration_settings.SEND_RESET_PASSWORD_LINK_SERIALIZER_CLASS
    deprecated = (
        hasattr(serializer_class, 'get_user_or_none')
        and callable(serializer_class.get_user_or_none))
    return not deprecated


# TODO: Issue #114 - remove deprecation check
@register()
@predicate_check(
    'REGISTER_EMAIL_SERIALIZER_CLASS contains deprecated get_email method,'
    ' which will be removed in version 0.7.0',
    WarningCode.DEPRECATION
)
def deprecated_register_email_serializer_check() -> bool:
    serializer_class = registration_settings.REGISTER_EMAIL_SERIALIZER_CLASS
    deprecated = (
        hasattr(serializer_class, 'get_email')
        and callable(serializer_class.get_email))
    return not deprecated


@register()
@predicate_check(
    'REGISTER_EMAIL_SERIALIZER_CLASS does not contain email field',
    ErrorCode.INVALID_REGISTER_EMAIL_SERIALIZER_CLASS
)
def valid_register_email_serializer_check() -> bool:
    serializer_class = registration_settings.REGISTER_EMAIL_SERIALIZER_CLASS
    serializer = serializer_class()
    try:
        return bool(serializer.fields['email'])
    except KeyError:
        return False


@register()
@predicate_check(
    'SEND_RESET_PASSWORD_LINK_SERIALIZER_USE_EMAIL is set'
    ' but email field is not unique',
    ErrorCode.NON_UNIQUE_FIELD_USED_AS_UNIQUE
)
def send_reset_password_link_serializer_email_unique_check() -> bool:
    return implies(
        registration_settings.SEND_RESET_PASSWORD_LINK_SERIALIZER_USE_EMAIL,
        _is_email_field_unique,
    )


def _is_email_field_unique() -> bool:
    user_cls = get_user_model()  # type: Type[Model]
    user_meta = user_cls._meta  # pylint: disable=protected-access
    email_field_name = get_user_email_field_name()
    return is_model_field_unique(user_meta.get_field(email_field_name))


def _is_auth_token_manager_proper_subclass() -> bool:
    cls = registration_settings.AUTH_TOKEN_MANAGER_CLASS
    return (
        issubclass(cls, AbstractAuthTokenManager)
        and cls != AbstractAuthTokenManager)


def _is_auth_token_manager_class_implementing_method(method_name: str) -> bool:
    cls = registration_settings.AUTH_TOKEN_MANAGER_CLASS
    cls_method = getattr(cls, method_name, None)
    abstract_method = getattr(AbstractAuthTokenManager, method_name)
    return cls_method is not abstract_method


def _is_auth_installed() -> bool:
    return 'django.contrib.auth' in settings.INSTALLED_APPS

from django.apps import apps
from django.core.checks.registry import registry
from django.test import TestCase
from django.test.utils import override_settings

from rest_registration.apps import RestRegistrationConfig
from rest_registration.auth_token_managers import AbstractAuthTokenManager
from rest_registration.checks import ErrorCode, WarningCode
from rest_registration.settings import DEFAULTS
from tests.helpers.settings import override_rest_registration_settings


def simulate_checks():
    app_configs = apps.app_configs
    errors = []
    all_checks = registry.get_checks(False)
    rest_registration_checks = [
        check for check in all_checks
        if check.__module__.startswith('rest_registration.')
    ]
    for check in rest_registration_checks:
        errors.extend(check(app_configs))
    return errors


class ChecksTestCase(TestCase):

    @override_settings(REST_REGISTRATION=DEFAULTS)
    def test_checks_default(self):
        errors = simulate_checks()
        self.assert_error_codes_match(errors, [
            ErrorCode.NO_REGISTER_EMAIL_VER_URL,
            ErrorCode.NO_REGISTER_VER_URL,
            ErrorCode.NO_RESET_PASSWORD_VER_URL,
            ErrorCode.NO_VER_FROM_EMAIL,
        ])

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_VERIFICATION_ENABLED': False,
            'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
            'RESET_PASSWORD_VERIFICATION_ENABLED': False,
        },
    )
    def test_checks_minimal_setup(self):
        errors = simulate_checks()
        self.assert_error_codes_match(errors, [])

    @override_settings(
        TEMPLATES=(),
        REST_REGISTRATION={
            'REGISTER_VERIFICATION_ENABLED': False,
            'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
            'RESET_PASSWORD_VERIFICATION_ENABLED': False,
        },
    )
    def test_checks_no_templates_minimal_setup(self):
        errors = simulate_checks()
        self.assert_error_codes_match(errors, [])

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_VERIFICATION_URL': '/verify-account/',
            'REGISTER_EMAIL_VERIFICATION_URL': '/verify-email/',
            'RESET_PASSWORD_VERIFICATION_URL': '/reset-password/',
            'VERIFICATION_FROM_EMAIL': 'jon.doe@example.com',
        },
    )
    def test_checks_preferred_setup(self):
        errors = simulate_checks()
        self.assert_error_codes_match(errors, [])

    @override_settings(
        TEMPLATES=(),
        REST_REGISTRATION={
            'REGISTER_VERIFICATION_URL': '/verify-account/',
            'REGISTER_EMAIL_VERIFICATION_URL': '/verify-email/',
            'RESET_PASSWORD_VERIFICATION_URL': '/reset-password/',
            'VERIFICATION_FROM_EMAIL': 'jon.doe@example.com',
        },
    )
    def test_checks_no_templates_preferred_setup(self):
        errors = simulate_checks()
        self.assert_error_codes_match(errors, [
            ErrorCode.INVALID_EMAIL_TEMPLATE_CONFIG,
            ErrorCode.INVALID_EMAIL_TEMPLATE_CONFIG,
            ErrorCode.INVALID_EMAIL_TEMPLATE_CONFIG,
        ])

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_VERIFICATION_URL': '/verify-account/',
            'REGISTER_EMAIL_VERIFICATION_URL': '/verify-email/',
            'RESET_PASSWORD_VERIFICATION_URL': '/reset-password/',
        },
    )
    def test_checks_preferred_setup_missing_sender_email(self):
        errors = simulate_checks()
        self.assert_error_codes_match(errors, [
            ErrorCode.NO_VER_FROM_EMAIL,
        ])

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_VERIFICATION_URL': '/verify-account/',
            'REGISTER_VERIFICATION_AUTO_LOGIN': True,
            'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
            'RESET_PASSWORD_VERIFICATION_ENABLED': False,
            'VERIFICATION_FROM_EMAIL': 'jon.doe@example.com',
        },
    )
    def test_checks_multiple_time_auto_login(self):
        errors = simulate_checks()
        self.assert_error_codes_match(errors, [
            WarningCode.REGISTER_VERIFICATION_MULTIPLE_AUTO_LOGIN,
        ])

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_VERIFICATION_ENABLED': False,
            'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
            'RESET_PASSWORD_VERIFICATION_URL': '/reset-password/',
        },
    )
    def test_checks_one_verification_url_missing_sender_email(self):
        errors = simulate_checks()
        self.assert_error_codes_match(errors, [
            ErrorCode.NO_VER_FROM_EMAIL,
        ])

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_VERIFICATION_URL': '/verify-account/',
            'REGISTER_EMAIL_VERIFICATION_URL': '/verify-email/',
            'RESET_PASSWORD_VERIFICATION_URL': '/reset-password/',
            'VERIFICATION_FROM_EMAIL': 'jon.doe@example.com',
            'LOGIN_RETRIEVE_TOKEN': True,
        },
    )
    def test_checks_missing_token_auth_config(self):
        errors = simulate_checks()
        self.assert_error_codes_match(errors, [
            ErrorCode.NO_TOKEN_AUTH_CONFIG,
        ])

    @override_settings(
        INSTALLED_APPS=(
            'django.contrib.admin',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',

            'rest_framework',
            'rest_registration',
        ),
        REST_REGISTRATION={
            'REGISTER_VERIFICATION_ENABLED': False,
            'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
            'RESET_PASSWORD_VERIFICATION_ENABLED': False,
        },
    )
    def test_checks_missing_auth_installed(self):
        errors = simulate_checks()
        self.assert_error_codes_match(errors, [
            ErrorCode.NO_AUTH_INSTALLED,
        ])

    @override_settings(
        INSTALLED_APPS=(
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',

            'rest_framework',
            'rest_registration',
        ),
        REST_REGISTRATION={
            'REGISTER_VERIFICATION_URL': '/verify-account/',
            'REGISTER_EMAIL_VERIFICATION_URL': '/verify-email/',
            'RESET_PASSWORD_VERIFICATION_URL': '/reset-password/',
            'VERIFICATION_FROM_EMAIL': 'jon.doe@example.com',
            'LOGIN_RETRIEVE_TOKEN': True,
        },
    )
    def test_checks_missing_token_auth_installed(self):
        errors = simulate_checks()
        self.assert_error_codes_match(errors, [
            ErrorCode.NO_TOKEN_AUTH_CONFIG,
            ErrorCode.NO_TOKEN_AUTH_INSTALLED,
        ])

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_VERIFICATION_URL': '/verify-account/',
            'REGISTER_EMAIL_VERIFICATION_URL': '/verify-email/',
            'RESET_PASSWORD_VERIFICATION_URL': '/reset-password/',
            'VERIFICATION_FROM_EMAIL': 'jon.doe@example.com',
            'REGISTER_VERIFICATION_EMAIL_TEMPLATES': {},
        },
    )
    def test_checks_invalid_register_verification_email_templates_config(self):
        errors = simulate_checks()
        self.assert_error_codes_match(errors, [
            ErrorCode.INVALID_EMAIL_TEMPLATE_CONFIG,
        ])

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_VERIFICATION_URL': '/verify-account/',
            'REGISTER_EMAIL_VERIFICATION_URL': '/verify-email/',
            'RESET_PASSWORD_VERIFICATION_URL': '/reset-password/',
            'VERIFICATION_FROM_EMAIL': 'jon.doe@example.com',
            'RESET_PASSWORD_VERIFICATION_EMAIL_TEMPLATES': {},
        },
    )
    def test_checks_invalid_register_email_verification_email_templates_config(self):  # noqa: E501
        errors = simulate_checks()
        self.assert_error_codes_match(errors, [
            ErrorCode.INVALID_EMAIL_TEMPLATE_CONFIG,
        ])

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_VERIFICATION_URL': '/verify-account/',
            'REGISTER_EMAIL_VERIFICATION_URL': '/verify-email/',
            'RESET_PASSWORD_VERIFICATION_URL': '/reset-password/',
            'VERIFICATION_FROM_EMAIL': 'jon.doe@example.com',
            'RESET_PASSWORD_VERIFICATION_EMAIL_TEMPLATES': {},
        },
    )
    def test_checks_invalid_reset_password_verification_email_templates_config(self):  # noqa: E501
        errors = simulate_checks()
        self.assert_error_codes_match(errors, [
            ErrorCode.INVALID_EMAIL_TEMPLATE_CONFIG,
        ])

    @override_settings(
        AUTHENTICATION_BACKENDS=[
            'django.contrib.auth.backends.AllowAllUsersModelBackend',
        ],
        REST_REGISTRATION={
            'REGISTER_VERIFICATION_ENABLED': False,
            'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
            'RESET_PASSWORD_VERIFICATION_ENABLED': False,
        },
    )
    def test_checks_invalid_auth_model_backend_used(self):
        errors = simulate_checks()
        self.assert_error_codes_match(errors, [
            ErrorCode.DRF_INCOMPATIBLE_DJANGO_AUTH_BACKEND,
        ])

    @override_settings(
        AUTHENTICATION_BACKENDS=[
            'django.contrib.auth.backends.AllowAllUsersRemoteUserBackend',
        ],
        REST_REGISTRATION={
            'REGISTER_VERIFICATION_ENABLED': False,
            'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
            'RESET_PASSWORD_VERIFICATION_ENABLED': False,
        },
    )
    def test_checks_invalid_auth_remote_backend_used(self):
        errors = simulate_checks()
        self.assert_error_codes_match(errors, [
            ErrorCode.DRF_INCOMPATIBLE_DJANGO_AUTH_BACKEND,
        ])

    def assert_error_codes_match(self, errors, expected_error_codes):
        assert_error_codes_match(errors, expected_error_codes)


@override_rest_registration_settings({
    'USER_LOGIN_FIELDS': ['username'],
})
def test_when_one_unique_login_field_then_check_succeeds():
    errors = simulate_checks()
    assert_error_codes_match(errors, [])


@override_rest_registration_settings({
    'USER_LOGIN_FIELDS': ['email'],
})
def test_when_one_non_unique_login_field_then_check_fails():
    errors = simulate_checks()
    assert_error_codes_match(errors, [
        ErrorCode.LOGIN_FIELDS_NOT_UNIQUE,
    ])


@override_rest_registration_settings({
    'USER_LOGIN_FIELDS': ['username', 'email'],
})
def test_when_one_non_unique_login_field_in_many_then_check_fails():
    errors = simulate_checks()
    assert_error_codes_match(errors, [
        ErrorCode.LOGIN_FIELDS_NOT_UNIQUE,
    ])


@override_rest_registration_settings({
    'AUTH_TOKEN_MANAGER_CLASS': 'tests.testapps.custom_authtokens.auth.FaultyAuthTokenManager',  # noqa: E501
})
def test_when_custom_authtokenmanager_wrt_specs_then_check_succeeds():
    errors = simulate_checks()
    assert_error_codes_match(errors, [])


class InvalidAuthTokenManager:  # pylint: disable=too-few-public-methods
    pass


class NotImplementedAuthTokenManager(AbstractAuthTokenManager):  # noqa: E501 pylint: disable=too-few-public-methods,abstract-method
    pass


@override_rest_registration_settings({
    'AUTH_TOKEN_MANAGER_CLASS': InvalidAuthTokenManager,
})
def test_when_authtokenmanager_is_not_correct_subclass_then_check_fails():
    errors = simulate_checks()
    assert_error_codes_match(errors, [
        ErrorCode.INVALID_AUTH_TOKEN_MANAGER_CLASS,
    ])


@override_rest_registration_settings({
    'AUTH_TOKEN_MANAGER_CLASS': NotImplementedAuthTokenManager,
})
def test_when_authtokenmanager_does_not_implement_methods_then_check_fails():
    errors = simulate_checks()
    assert_error_codes_match(errors, [
        ErrorCode.INVALID_AUTH_TOKEN_MANAGER_CLASS,
        ErrorCode.INVALID_AUTH_TOKEN_MANAGER_CLASS,
    ])
    expected_messages = {
        "AUTH_TOKEN_MANAGER_CLASS is not implementing method get_authentication_class",  # noqa: E501
        "AUTH_TOKEN_MANAGER_CLASS is not implementing method provide_token",
    }
    assert {e.msg for e in errors} == expected_messages


def assert_error_codes_match(errors, expected_error_codes):
    error_ids = sorted(e.id for e in errors)
    expected_error_ids = sorted(
        '{RestRegistrationConfig.name}.{code}'.format(
            RestRegistrationConfig=RestRegistrationConfig,
            code=code)
        for code in expected_error_codes)
    msg = "\n\nList of errors:\n"
    for error in errors:
        msg += "- {error}\n".format(error=error)
    msg += " does not match the codes: "
    if expected_error_codes:
        msg += ", ".join(str(e) for e in expected_error_codes)
    else:
        msg += "(empty list)"
    assert error_ids == expected_error_ids, msg

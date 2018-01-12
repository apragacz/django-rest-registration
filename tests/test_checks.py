from django.apps import apps
from django.test import TestCase
from django.test.utils import override_settings

from rest_registration.apps import RestRegistrationConfig
from rest_registration.settings import DEFAULTS
from rest_registration.checks import __ALL_CHECKS__, ErrorCode


def simulate_checks():
    app_configs = apps.app_configs
    errors = []
    for check in __ALL_CHECKS__:
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
            'REGISTER_VERIFICATION_URL': '/verify-account/',
            'REGISTER_EMAIL_VERIFICATION_URL': '/verify-email/',
            'RESET_PASSWORD_VERIFICATION_URL': '/reset-password/',
            'VERIFICATION_FROM_EMAIL': 'jon.doe@example.com',
        }
    )
    def test_checks_minimal_setup(self):
        errors = simulate_checks()
        self.assert_error_codes_match(errors, [])

    def assert_error_codes_match(self, errors, expected_error_codes):
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
        self.assertListEqual(error_ids, expected_error_ids, msg=msg)

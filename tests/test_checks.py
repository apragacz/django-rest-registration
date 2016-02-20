from django.apps import apps
from django.test import TestCase
from django.test.utils import override_settings

from rest_registration.checks import __ALL_CHECKS__


def simulate_checks():
    app_configs = apps.app_configs
    errors = []
    for check in __ALL_CHECKS__:
        errors.extend(check(app_configs))
    return errors


class ChecksTestCase(TestCase):

    def test_checks_default(self):
        errors = simulate_checks()
        self.assertEqual(len(errors), 4)

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_VERIFICATION_URL': '/verify-account/',
            'REGISTER_EMAIL_VERIFICATION_URL': '/verify-email/',
            'RESET_PASSWORD_VERIFICATION_URL': '/reset-password/',
            'VERIFICATION_FROM_EMAIL': 'jon.doe@example.com',
        }
    )
    def test_checks_minmal_setup(self):
        errors = simulate_checks()
        self.assertEqual(len(errors), 0)

from django.test import TestCase
from django.test.utils import override_settings

from rest_registration.settings import NestedSettings


class RegistrationSettingsTestCase(TestCase):

    def setUp(self):
        self.defaults = {
            'A': 2,
            'B': 3,
        }

    def test_user_settings(self):
        user_settings = {
            'A': 1,
        }
        settings = NestedSettings(
            user_settings, self.defaults, (), 'NESTED_TEST_SETTING')
        self.assertEqual(settings.A, 1)
        self.assertEqual(settings.B, 3)

    @override_settings(
        REST_REGISTRATION={
            'A': 5,
        }
    )
    def test_django_settings(self):
        settings = NestedSettings(
            None, self.defaults, (), 'REST_REGISTRATION')
        self.assertEqual(settings.A, 5)
        self.assertEqual(settings.B, 3)

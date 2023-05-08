from django.test.utils import override_settings

from rest_registration.api.views.register import RegisterSigner

from .base import ViewTestCase

VERIFICATION_URL = '/accounts/verify-account/'
SUCCESS_URL = '/accounts/verify-account/success/'
FAILURE_URL = '/accounts/verify-account/failure/'


@override_settings(
    REST_REGISTRATION={
        'REGISTER_VERIFICATION_ENABLED': True,
        'REGISTER_VERIFICATION_URL': VERIFICATION_URL,
    },
    REST_REGISTRATION_VERIFICATION_REDIRECTS={
        'VERIFY_REGISTRATION_SUCCESS_URL': SUCCESS_URL,
        'VERIFY_REGISTRATION_FAILURE_URL': FAILURE_URL,
    },
)
class VerifyRegistrationTestCase(ViewTestCase):
    VIEW_NAME = 'verify-registration'

    def test_ok(self):
        user = self.create_test_user(is_active=False)
        self.assertFalse(user.is_active)
        signer = RegisterSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        response = self.client.get(self.view_url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, SUCCESS_URL)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_tampered_signature(self):
        user = self.create_test_user(is_active=False)
        self.assertFalse(user.is_active)
        signer = RegisterSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        data['signature'] += 'blah'
        response = self.client.get(self.view_url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, FAILURE_URL)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

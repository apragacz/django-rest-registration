from django.test.utils import override_settings

from rest_registration.api.views.reset_password import ResetPasswordSigner

from .base import ViewTestCase

VERIFICATION_URL = '/accounts/reset-password/'
SUCCESS_URL = '/accounts/reset-password/success/'
FAILURE_URL = '/accounts/reset-password/failure/'


@override_settings(
    REST_REGISTRATION={
        'RESET_PASSWORD_VERIFICATION_URL': VERIFICATION_URL,
    },
    REST_REGISTRATION_VERIFICATION_REDIRECTS={
        'RESET_PASSWORD_SUCCESS_URL': SUCCESS_URL,
        'RESET_PASSWORD_FAILURE_URL': FAILURE_URL,
    },
)
class ResetPasswordTestCase(ViewTestCase):
    VIEW_NAME = 'reset-password'

    def test_ok(self):
        old_password = 'password1'
        new_password = 'eaWrivtig5'
        user = self.create_test_user(password=old_password)
        signer = ResetPasswordSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        data['password'] = new_password
        response = self.client.post(self.view_url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, SUCCESS_URL)
        user.refresh_from_db()
        self.assertTrue(user.check_password(new_password))

    def test_tampered_signature(self):
        old_password = 'password1'
        new_password = 'eaWrivtig5'
        user = self.create_test_user(password=old_password)
        signer = ResetPasswordSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        data['password'] = new_password
        data['signature'] += 'heh'
        response = self.client.post(self.view_url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, FAILURE_URL)
        user.refresh_from_db()
        self.assertTrue(user.check_password(old_password))

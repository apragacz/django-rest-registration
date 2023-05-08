from django.test.utils import override_settings

from rest_registration.api.views.register_email import RegisterEmailSigner

from .base import ViewTestCase

VERIFICATION_URL = '/accounts/verify-email/'
SUCCESS_URL = '/accounts/verify-email/success/'
FAILURE_URL = '/accounts/verify-email/failure/'


@override_settings(
    REST_REGISTRATION={
        'REGISTER_EMAIL_VERIFICATION_ENABLED': True,
        'REGISTER_EMAIL_VERIFICATION_URL': VERIFICATION_URL,
    },
    REST_REGISTRATION_VERIFICATION_REDIRECTS={
        'VERIFY_EMAIL_SUCCESS_URL': SUCCESS_URL,
        'VERIFY_EMAIL_FAILURE_URL': FAILURE_URL,
    },
)
class VerifyEmailTestCase(ViewTestCase):
    VIEW_NAME = 'verify-email'

    def setUp(self):
        super().setUp()
        self.email = 'testuser1@example.com'
        self.new_email = 'testuser2@example.com'
        self.user = self.create_test_user(email=self.email)

    def test_ok(self):
        signer = RegisterEmailSigner({
            'user_id': self.user.pk,
            'email': self.new_email,
        })
        data = signer.get_signed_data()
        response = self.client.get(self.view_url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, SUCCESS_URL)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.new_email)

    def test_tampered_signature(self):
        signer = RegisterEmailSigner({
            'user_id': self.user.pk,
            'email': self.new_email,
        })
        data = signer.get_signed_data()
        data['signature'] += 'ech'
        response = self.client.get(self.view_url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, FAILURE_URL)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.email)

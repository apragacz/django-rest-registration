import math
import time
from unittest.mock import patch

from django.test.utils import override_settings
from rest_framework import status
from rest_framework.test import force_authenticate

from rest_registration.api.views.register_email import RegisterEmailSigner

from .base import APIViewTestCase

REGISTER_EMAIL_VERIFICATION_URL = '/verify-email/'
REST_REGISTRATION_WITH_EMAIL_VERIFICATION = {
    'REGISTER_EMAIL_VERIFICATION_ENABLED': True,
    'REGISTER_EMAIL_VERIFICATION_URL': REGISTER_EMAIL_VERIFICATION_URL,
    'VERIFICATION_FROM_EMAIL': 'no-reply@example.com',
}


class BaseRegisterEmailViewTestCase(APIViewTestCase):

    def setUp(self):
        super().setUp()
        self.email = 'testuser1@example.com'
        self.new_email = 'testuser2@example.com'
        self.user = self.create_test_user(email=self.email)


class RegisterEmailViewTestCase(BaseRegisterEmailViewTestCase):
    VIEW_NAME = 'register-email'

    def _test_authenticated(self, data):
        request = self.create_post_request(data)
        force_authenticate(request, user=self.user)
        response = self.view_func(request)
        return response

    @override_settings(
        REST_REGISTRATION=REST_REGISTRATION_WITH_EMAIL_VERIFICATION,
    )
    def test_ok(self):
        data = {
            'email': self.new_email,
        }
        time_before = math.floor(time.time())
        with self.assert_one_mail_sent() as sent_emails:
            response = self._test_authenticated(data)
            self.assert_valid_response(response, status.HTTP_200_OK)
        time_after = math.ceil(time.time())
        # Check database state.
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.email)
        # Check verification e-mail.
        sent_email = sent_emails[0]
        self.assertEqual(
            sent_email.from_email,
            REST_REGISTRATION_WITH_EMAIL_VERIFICATION['VERIFICATION_FROM_EMAIL'],  # noqa: E501
        )
        self.assertListEqual(sent_email.to, [self.new_email])
        url = self.assert_one_url_line_in_text(sent_email.body)
        verification_data = self.assert_valid_verification_url(
            url,
            expected_path=REGISTER_EMAIL_VERIFICATION_URL,
            expected_query_keys={'signature', 'user_id', 'timestamp', 'email'},
        )
        self.assertEqual(verification_data['email'], self.new_email)
        self.assertEqual(int(verification_data['user_id']), self.user.id)
        url_sig_timestamp = int(verification_data['timestamp'])
        self.assertGreaterEqual(url_sig_timestamp, time_before)
        self.assertLessEqual(url_sig_timestamp, time_after)
        signer = RegisterEmailSigner(verification_data)
        signer.verify()

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_EMAIL_VERIFICATION_ENABLED': False
        }
    )
    def test_noverify_ok(self):
        data = {
            'email': self.new_email,
        }
        with self.assert_no_mail_sent():
            response = self._test_authenticated(data)
            self.assert_valid_response(response, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.new_email)


class VerifyEmailViewTestCase(BaseRegisterEmailViewTestCase):
    VIEW_NAME = 'verify-email'

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_EMAIL_VERIFICATION_URL': REGISTER_EMAIL_VERIFICATION_URL,
        }
    )
    def test_ok(self):
        signer = RegisterEmailSigner({
            'user_id': self.user.pk,
            'email': self.new_email,
        })
        data = signer.get_signed_data()
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_valid_response(response, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.new_email)

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
        }
    )
    def test_noverify_not_found(self):
        signer = RegisterEmailSigner({
            'user_id': self.user.pk,
            'email': self.new_email,
        }, strict=False)
        data = signer.get_signed_data()
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_invalid_response(response, status.HTTP_404_NOT_FOUND)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.email)

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_EMAIL_VERIFICATION_URL': REGISTER_EMAIL_VERIFICATION_URL,
        }
    )
    def test_tampered_timestamp(self):
        signer = RegisterEmailSigner({
            'user_id': self.user.pk,
            'email': self.new_email,
        })
        data = signer.get_signed_data()
        data['timestamp'] += 1
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_invalid_response(response, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.email)

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_EMAIL_VERIFICATION_URL': REGISTER_EMAIL_VERIFICATION_URL,
        }
    )
    def test_tampered_email(self):
        signer = RegisterEmailSigner({
            'user_id': self.user.pk,
            'email': self.new_email,
        })
        data = signer.get_signed_data()
        data['email'] = 'p' + data['email']
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_invalid_response(response, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.email)

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_EMAIL_VERIFICATION_URL': REGISTER_EMAIL_VERIFICATION_URL,
        }
    )
    def test_expired(self):
        timestamp = time.time()
        with patch('time.time',
                   side_effect=lambda: timestamp):
            signer = RegisterEmailSigner({
                'user_id': self.user.pk,
                'email': self.new_email,
            })
            data = signer.get_signed_data()
        request = self.create_post_request(data)
        with patch('time.time',
                   side_effect=lambda: timestamp + 3600 * 24 * 8):
            response = self.view_func(request)
        self.assert_invalid_response(response, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.email)

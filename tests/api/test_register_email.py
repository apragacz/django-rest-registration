import time
from unittest.mock import patch

from django.test.utils import override_settings
from rest_framework import status
from rest_framework.test import force_authenticate

from rest_registration.api.views import register_email, verify_email
from rest_registration.api.views.register_email import RegisterEmailSigner
from .base import APIViewTestCase


REGISTER_EMAIL_VERIFICATION_URL = '/verify-email/'


class BaseRegisterEmailViewTestCase(APIViewTestCase):

    def setUp(self):
        super().setUp()
        self.email = 'testuser1@example.com'
        self.new_email = 'testuser2@example.com'
        self.user = self.create_test_user(email=self.email)


class RegisterEmailViewTestCase(BaseRegisterEmailViewTestCase):

    def _test_authenticated(self, data):
        request = self.factory.post('', data)
        force_authenticate(request, user=self.user)
        response = register_email(request)
        return response

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_EMAIL_VERIFICATION_URL': REGISTER_EMAIL_VERIFICATION_URL,
        }
    )
    def test_ok(self):
        data = {
            'email': self.new_email,
        }
        with self.assert_mail_sent():
            response = self._test_authenticated(data)
            self.assert_valid_response(response, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.email)

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
        request = self.factory.post('', data)
        response = verify_email(request)
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
        request = self.factory.post('', data)
        response = verify_email(request)
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
        request = self.factory.post('', data)
        response = verify_email(request)
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
        request = self.factory.post('', data)
        response = verify_email(request)
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
        request = self.factory.post('', data)
        with patch('time.time',
                   side_effect=lambda: timestamp + 3600 * 24 * 8):
            response = verify_email(request)
        self.assert_invalid_response(response, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.email)

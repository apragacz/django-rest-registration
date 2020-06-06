import time
from unittest.mock import patch

from django.test.utils import override_settings
from rest_framework import status

from rest_registration.api.views.register_email import RegisterEmailSigner
from tests.helpers.constants import (
    REGISTER_EMAIL_VERIFICATION_URL,
    VERIFICATION_FROM_EMAIL
)
from tests.helpers.settings import (
    override_auth_model_settings,
    override_rest_registration_settings
)

from ..base import APIViewTestCase

REST_REGISTRATION_WITH_EMAIL_VERIFICATION = {
    'REGISTER_EMAIL_VERIFICATION_ENABLED': True,
    'REGISTER_EMAIL_VERIFICATION_URL': REGISTER_EMAIL_VERIFICATION_URL,
    'VERIFICATION_FROM_EMAIL': VERIFICATION_FROM_EMAIL,
}


@override_rest_registration_settings({
    'REGISTER_EMAIL_VERIFICATION_ENABLED': True,
    'REGISTER_EMAIL_VERIFICATION_URL': REGISTER_EMAIL_VERIFICATION_URL,
    'VERIFICATION_FROM_EMAIL': VERIFICATION_FROM_EMAIL,
})
class VerifyEmailViewTestCase(APIViewTestCase):
    VIEW_NAME = 'verify-email'

    def setUp(self):
        super().setUp()
        self.email = 'testuser1@example.com'
        self.new_email = 'testuser2@example.com'
        self.user = None
        self.user2 = None

    def setup_user(self):
        user = self.create_test_user(
            username='testusername', email=self.email)
        self.user = user
        return user

    def setup_user2_with_user_new_email(self):
        user = self.create_test_user(
            username='testusername2', email=self.new_email)
        self.user2 = user
        return user

    def build_signer(self):
        signer = RegisterEmailSigner({
            'user_id': self.user.pk,
            'email': self.new_email,
        })
        return signer

    def assert_user_email_changed(self):
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.new_email)

    def assert_user_email_not_changed(self):
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, self.email)

    def test_ok(self):
        self.setup_user()
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

    def test_new_email_already_in_use_ok(self):
        self.setup_user()
        self.setup_user2_with_user_new_email()
        signer = self.build_signer()
        request = self.create_post_request(signer.get_signed_data())
        response = self.view_func(request)
        self.assert_response_is_ok(response)
        self.assert_user_email_changed()

    @override_rest_registration_settings({
        'USER_VERIFICATION_ID_FIELD': 'username',
    })
    def test_with_username_as_verification_id_ok(self):
        self.setup_user()
        signer = RegisterEmailSigner({
            'user_id': self.user.username,
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
            'REGISTER_EMAIL_VERIFICATION_URL': REGISTER_EMAIL_VERIFICATION_URL,
        }
    )
    def test_inactive_user(self):
        self.setup_user()
        old_email = self.user.email
        self.user.is_active = False
        self.user.save()
        signer = RegisterEmailSigner({
            'user_id': self.user.pk,
            'email': self.new_email,
        })
        data = signer.get_signed_data()
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_response_is_bad_request(response)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, old_email)

    @override_rest_registration_settings({
        'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
    })
    def test_noverify_not_found(self):
        self.setup_user()
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

    def test_tampered_timestamp(self):
        self.setup_user()
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

    def test_tampered_email(self):
        self.setup_user()
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

    def test_expired(self):
        self.setup_user()
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

    @override_auth_model_settings('custom_users.UserWithUniqueEmail')
    def test_user_with_unique_email_user_email_already_exists(self):
        self.setup_user()
        self.setup_user2_with_user_new_email()
        signer = self.build_signer()
        request = self.create_post_request(signer.get_signed_data())
        response = self.view_func(request)
        self.assert_response_is_bad_request(response)
        self.assert_user_email_not_changed()

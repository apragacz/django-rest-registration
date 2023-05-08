import time
from unittest import mock
from unittest.mock import patch

from rest_framework import status

from rest_registration.api.views.register import RegisterSigner
from tests.helpers.constants import REGISTER_VERIFICATION_URL, VERIFICATION_FROM_EMAIL
from tests.helpers.settings import override_rest_registration_settings

from ..base import APIViewTestCase


@override_rest_registration_settings({
    'REGISTER_VERIFICATION_ENABLED': True,
    'REGISTER_VERIFICATION_URL': REGISTER_VERIFICATION_URL,
    'VERIFICATION_FROM_EMAIL': VERIFICATION_FROM_EMAIL,
})
class VerifyRegistrationViewTestCase(APIViewTestCase):
    VIEW_NAME = 'verify-registration'

    def prepare_user(self):
        user = self.create_test_user(is_active=False)
        self.assertFalse(user.is_active)
        return user

    def prepare_request(self, user, session=False, data_to_sign=None):
        if data_to_sign is None:
            data_to_sign = {'user_id': user.pk}
        signer = RegisterSigner(data_to_sign)
        data = signer.get_signed_data()
        request = self.create_post_request(data)
        if session:
            self.add_session_to_request(request)
        return request

    def prepare_user_and_request(self, session=False):
        user = self.prepare_user()
        request = self.prepare_request(user, session=session)
        return user, request

    def test_verify_ok(self):
        user, request = self.prepare_user_and_request()
        response = self.view_func(request)
        self.assert_valid_response(response, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    @override_rest_registration_settings({
        'USER_VERIFICATION_ID_FIELD': 'username',
    })
    def test_verify_with_username_as_verification_id_ok(self):
        user = self.prepare_user()
        request = self.prepare_request(
            user, data_to_sign={'user_id': user.username})
        response = self.view_func(request)
        self.assert_valid_response(response, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_verify_ok_idempotent(self):
        user = self.prepare_user()
        request1 = self.prepare_request(user)
        request2 = self.prepare_request(user)

        self.view_func(request1)

        response = self.view_func(request2)
        self.assert_valid_response(response, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    @override_rest_registration_settings({
        'REGISTER_VERIFICATION_ONE_TIME_USE': True,
    })
    def test_verify_one_time_use(self):
        user = self.prepare_user()
        request1 = self.prepare_request(user)
        request2 = self.prepare_request(user)

        self.view_func(request1)

        response = self.view_func(request2)
        self.assert_valid_response(response, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    @override_rest_registration_settings({
        'REGISTER_VERIFICATION_AUTO_LOGIN': True,
    })
    def test_verify_ok_login(self):
        with patch('django.contrib.auth.login') as login_mock:
            user, request = self.prepare_user_and_request()
            response = self.view_func(request)
            login_mock.assert_called_once_with(
                mock.ANY,
                user,
                backend='django.contrib.auth.backends.ModelBackend')
        self.assert_valid_response(response, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_verify_tampered_timestamp(self):
        user = self.create_test_user(is_active=False)
        self.assertFalse(user.is_active)
        signer = RegisterSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        data['timestamp'] += 1
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_invalid_response(response, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_verify_expired(self):
        timestamp = int(time.time())
        user = self.create_test_user(is_active=False)
        self.assertFalse(user.is_active)
        with patch('time.time',
                   side_effect=lambda: timestamp):
            signer = RegisterSigner({'user_id': user.pk})
            data = signer.get_signed_data()
            request = self.create_post_request(data)
        with patch('time.time',
                   side_effect=lambda: timestamp + 3600 * 24 * 8):
            response = self.view_func(request)
        self.assert_invalid_response(response, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    @override_rest_registration_settings({
        'REGISTER_VERIFICATION_ENABLED': False,
        'REGISTER_VERIFICATION_URL': REGISTER_VERIFICATION_URL,
    })
    def test_verify_disabled(self):
        user, request = self.prepare_user_and_request()
        response = self.view_func(request)

        self.assert_invalid_response(response, status.HTTP_404_NOT_FOUND)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

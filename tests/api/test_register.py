import time
from unittest.mock import patch

from django.test.utils import override_settings
from rest_framework import status

from rest_registration.api.views import register, verify_registration
from rest_registration.api.views.register import RegisterSigner
from rest_registration.settings import registration_settings

from .base import APIViewTestCase

REGISTER_VERIFICATION_URL = '/verify-account/'
REST_REGISTRATION_WITH_VERIFICATION = {
    'REGISTER_VERIFICATION_ENABLED': True,
    'REGISTER_VERIFICATION_URL': REGISTER_VERIFICATION_URL,
    'VERIFICATION_FROM_EMAIL': 'no-reply@example.com',
}


@override_settings(REST_REGISTRATION=REST_REGISTRATION_WITH_VERIFICATION)
class RegisterViewTestCase(APIViewTestCase):

    def test_register_serializer_ok(self):
        serializer_class = registration_settings.REGISTER_SERIALIZER_CLASS
        serializer = serializer_class(data={})
        field_names = {f for f in serializer.get_fields()}
        self.assertEqual(
            field_names,
            {'username', 'first_name', 'last_name', 'email',
             'password', 'password_confirm'},
        )

    def test_register_ok(self):
        data = self._get_register_user_data(password='testpassword')
        request = self.factory.post('', data)
        with self.assert_mail_sent():
            response = register(request)
        self.assert_valid_response(response, status.HTTP_201_CREATED)
        user_id = response.data['id']
        user = self.user_class.objects.get(id=user_id)
        self.assertEqual(user.username, data['username'])
        self.assertTrue(user.check_password(data['password']))
        self.assertFalse(user.is_active)

    def test_register_no_email(self):
        data = self._get_register_user_data(password='testpassword', email='')
        request = self.factory.post('', data)
        with self.assert_no_mail_sent():
            response = register(request)
            self.assert_response_is_bad_request(response)

    def test_register_short_password(self):
        data = self._get_register_user_data(password='a')
        request = self.factory.post('', data)
        with self.assert_no_mail_sent():
            response = register(request)
            self.assert_response_is_bad_request(response)

    def test_register_password_numeric(self):
        data = self._get_register_user_data(password='4321332211113322')
        request = self.factory.post('', data)
        with self.assert_no_mail_sent():
            response = register(request)
            self.assert_response_is_bad_request(response)

    def test_register_password_same_as_username(self):
        username = 'testusername'
        data = self._get_register_user_data(
            username=username, password=username)
        request = self.factory.post('', data)
        with self.assert_no_mail_sent():
            response = register(request)
            self.assert_response_is_bad_request(response)

    def test_register_not_matching_password(self):
        data = self._get_register_user_data(
            password='testpassword1',
            password_confirm='testpassword2')
        request = self.factory.post('', data)
        with self.assert_no_mail_sent():
            response = register(request)
            self.assert_response_is_bad_request(response)

    def _get_register_user_data(
            self, password, password_confirm=None, **options):
        username = 'testusername'
        email = 'testusername@example.com'
        if password_confirm is None:
            password_confirm = password
        data = {
            'username': username,
            'password': password,
            'password_confirm': password_confirm,
            'email': email,
        }
        data.update(options)
        return data


class VerifyRegistrationViewTestCase(APIViewTestCase):

    @override_settings(REST_REGISTRATION=REST_REGISTRATION_WITH_VERIFICATION)
    def test_verify_ok(self):
        user = self.create_test_user(is_active=False)
        self.assertFalse(user.is_active)
        signer = RegisterSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        request = self.factory.post('', data)
        response = verify_registration(request)
        self.assert_valid_response(response, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    @override_settings(REST_REGISTRATION=REST_REGISTRATION_WITH_VERIFICATION)
    def test_verify_tampered_timestamp(self):
        user = self.create_test_user(is_active=False)
        self.assertFalse(user.is_active)
        signer = RegisterSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        data['timestamp'] += 1
        request = self.factory.post('', data)
        response = verify_registration(request)
        self.assert_invalid_response(response, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    @override_settings(REST_REGISTRATION=REST_REGISTRATION_WITH_VERIFICATION)
    def test_verify_expired(self):
        timestamp = int(time.time())
        user = self.create_test_user(is_active=False)
        self.assertFalse(user.is_active)
        with patch('time.time',
                   side_effect=lambda: timestamp):
            signer = RegisterSigner({'user_id': user.pk})
            data = signer.get_signed_data()
            request = self.factory.post('', data)
        with patch('time.time',
                   side_effect=lambda: timestamp + 3600 * 24 * 8):
            response = verify_registration(request)
        self.assert_invalid_response(response, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_VERIFICATION_ENABLED': False,
            'REGISTER_VERIFICATION_URL': REGISTER_VERIFICATION_URL,
        }
    )
    def test_verify_disabled(self):
        user = self.create_test_user(is_active=False)
        self.assertFalse(user.is_active)
        signer = RegisterSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        request = self.factory.post('', data)
        response = verify_registration(request)
        self.assert_invalid_response(response, status.HTTP_404_NOT_FOUND)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

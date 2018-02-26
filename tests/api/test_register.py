import math
import time
from unittest.mock import patch

from django.test.utils import override_settings
from rest_framework import status

from rest_registration.api.views.register import RegisterSigner
from rest_registration.settings import registration_settings

from .base import APIViewTestCase

REGISTER_VERIFICATION_URL = '/verify-account/'
REST_REGISTRATION_WITH_VERIFICATION = {
    'REGISTER_VERIFICATION_ENABLED': True,
    'REGISTER_VERIFICATION_URL': REGISTER_VERIFICATION_URL,
    'VERIFICATION_FROM_EMAIL': 'no-reply@example.com',
}

REST_REGISTRATION_WITH_VERIFICATION_NO_PASSWORD = {
    'REGISTER_VERIFICATION_ENABLED': True,
    'REGISTER_VERIFICATION_URL': REGISTER_VERIFICATION_URL,
    'VERIFICATION_FROM_EMAIL': 'no-reply@example.com',
    'REGISTER_SERIALIZER_PASSWORD_CONFIRM': False,
}

REST_REGISTRATION_WITHOUT_VERIFICATION = {
    'REGISTER_VERIFICATION_ENABLED': False,
}


@override_settings(REST_REGISTRATION=REST_REGISTRATION_WITH_VERIFICATION)
class RegisterViewTestCase(APIViewTestCase):
    VIEW_NAME = 'register'

    def test_register_serializer_ok(self):
        serializer_class = registration_settings.REGISTER_SERIALIZER_CLASS
        serializer = serializer_class(data={})
        field_names = {f for f in serializer.get_fields()}
        self.assertEqual(
            field_names,
            {'username', 'first_name', 'last_name', 'email',
             'password', 'password_confirm'},
        )

    @override_settings(
        REST_REGISTRATION=REST_REGISTRATION_WITH_VERIFICATION_NO_PASSWORD,
    )
    def test_register_serializer_no_password_ok(self):
        serializer_class = registration_settings.REGISTER_SERIALIZER_CLASS
        serializer = serializer_class(data={})
        field_names = {f for f in serializer.get_fields()}
        self.assertEqual(
            field_names,
            {'username', 'first_name', 'last_name', 'email', 'password'},
        )

    def test_register_ok(self):
        data = self._get_register_user_data(password='testpassword')
        request = self.create_post_request(data)
        time_before = math.floor(time.time())
        with self.assert_one_mail_sent() as sent_emails:
            response = self.view_func(request)
        time_after = math.ceil(time.time())
        self.assert_valid_response(response, status.HTTP_201_CREATED)
        user_id = response.data['id']
        # Check database state.
        user = self.user_class.objects.get(id=user_id)
        self.assertEqual(user.username, data['username'])
        self.assertTrue(user.check_password(data['password']))
        self.assertFalse(user.is_active)
        # Check verification e-mail.
        sent_email = sent_emails[0]
        self.assertEqual(
            sent_email.from_email,
            REST_REGISTRATION_WITH_VERIFICATION['VERIFICATION_FROM_EMAIL'],
        )
        self.assertListEqual(sent_email.to, [data['email']])
        url = self.assert_one_url_line_in_text(sent_email.body)

        verification_data = self.assert_valid_verification_url(
            url,
            expected_path=REGISTER_VERIFICATION_URL,
            expected_query_keys={'signature', 'user_id', 'timestamp'},
        )
        url_user_id = int(verification_data['user_id'])
        self.assertEqual(url_user_id, user_id)
        url_sig_timestamp = int(verification_data['timestamp'])
        self.assertGreaterEqual(url_sig_timestamp, time_before)
        self.assertLessEqual(url_sig_timestamp, time_after)
        signer = RegisterSigner(verification_data)
        signer.verify()

    @override_settings(
        REST_REGISTRATION=REST_REGISTRATION_WITH_VERIFICATION_NO_PASSWORD,
    )
    def test_register_no_password_confirm_ok(self):
        data = self._get_register_user_data(password='testpassword')
        data.pop('password_confirm')
        request = self.create_post_request(data)
        time_before = math.floor(time.time())
        with self.assert_one_mail_sent() as sent_emails:
            response = self.view_func(request)
            self.assert_valid_response(response, status.HTTP_201_CREATED)
        time_after = math.ceil(time.time())
        user_id = response.data['id']
        # Check database state.
        user = self.user_class.objects.get(id=user_id)
        self.assertEqual(user.username, data['username'])
        self.assertTrue(user.check_password(data['password']))
        self.assertFalse(user.is_active)
        # Check verification e-mail.
        sent_email = sent_emails[0]
        self.assertEqual(
            sent_email.from_email,
            REST_REGISTRATION_WITH_VERIFICATION['VERIFICATION_FROM_EMAIL'],
        )
        self.assertListEqual(sent_email.to, [data['email']])
        url = self.assert_one_url_line_in_text(sent_email.body)

        verification_data = self.assert_valid_verification_url(
            url,
            expected_path=REGISTER_VERIFICATION_URL,
            expected_query_keys={'signature', 'user_id', 'timestamp'},
        )
        url_user_id = int(verification_data['user_id'])
        self.assertEqual(url_user_id, user_id)
        url_sig_timestamp = int(verification_data['timestamp'])
        self.assertGreaterEqual(url_sig_timestamp, time_before)
        self.assertLessEqual(url_sig_timestamp, time_after)
        signer = RegisterSigner(verification_data)
        signer.verify()

    def test_register_same_username(self):
        self.create_test_user(username='testusername')

        data = self._get_register_user_data(
            username='testusername', password='testpassword')
        request = self.create_post_request(data)
        with self.assert_no_mail_sent():
            response = self.view_func(request)
            self.assert_invalid_response(response, status.HTTP_400_BAD_REQUEST)

    @override_settings(
        REST_REGISTRATION=REST_REGISTRATION_WITHOUT_VERIFICATION,
    )
    def test_register_without_verification_ok(self):
        data = self._get_register_user_data(password='testpassword')
        request = self.create_post_request(data)
        with self.assert_no_mail_sent():
            response = self.view_func(request)
            self.assert_valid_response(response, status.HTTP_201_CREATED)
        user_id = response.data['id']
        user = self.user_class.objects.get(id=user_id)
        self.assertEqual(user.username, data['username'])
        self.assertTrue(user.check_password(data['password']))
        self.assertTrue(user.is_active)

    def test_register_missing_email(self):
        data = self._get_register_user_data(password='testpassword')
        del data['email']
        request = self.create_post_request(data)
        with self.assert_no_mail_sent():
            response = self.view_func(request)
            self.assert_invalid_response(response, status.HTTP_400_BAD_REQUEST)

    def test_register_empty_email(self):
        data = self._get_register_user_data(password='testpassword', email='')
        request = self.create_post_request(data)
        with self.assert_no_mail_sent():
            response = self.view_func(request)
            self.assert_response_is_bad_request(response)

    def test_register_short_password(self):
        data = self._get_register_user_data(password='a')
        request = self.create_post_request(data)
        with self.assert_no_mail_sent():
            response = self.view_func(request)
            self.assert_response_is_bad_request(response)

    def test_register_password_numeric(self):
        data = self._get_register_user_data(password='4321332211113322')
        request = self.create_post_request(data)
        with self.assert_no_mail_sent():
            response = self.view_func(request)
            self.assert_response_is_bad_request(response)

    def test_register_password_same_as_username(self):
        username = 'testusername'
        data = self._get_register_user_data(
            username=username, password=username)
        request = self.create_post_request(data)
        with self.assert_no_mail_sent():
            response = self.view_func(request)
            self.assert_response_is_bad_request(response)

    def test_register_not_matching_password(self):
        data = self._get_register_user_data(
            password='testpassword1',
            password_confirm='testpassword2')
        request = self.create_post_request(data)
        with self.assert_no_mail_sent():
            response = self.view_func(request)
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
    VIEW_NAME = 'verify-registration'

    @override_settings(REST_REGISTRATION=REST_REGISTRATION_WITH_VERIFICATION)
    def test_verify_ok(self):
        user = self.create_test_user(is_active=False)
        self.assertFalse(user.is_active)
        signer = RegisterSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        request = self.create_post_request(data)
        response = self.view_func(request)
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
        request = self.create_post_request(data)
        response = self.view_func(request)
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
            request = self.create_post_request(data)
        with patch('time.time',
                   side_effect=lambda: timestamp + 3600 * 24 * 8):
            response = self.view_func(request)
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
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_invalid_response(response, status.HTTP_404_NOT_FOUND)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

import time
from unittest import mock
from unittest.mock import patch
from urllib.parse import quote_plus as urlquote
from urllib.parse import unquote_plus as urlunquote
from urllib.parse import urlparse

import pytest
from django.core.mail.backends.base import BaseEmailBackend
from django.test.utils import override_settings
from rest_framework import status

from rest_registration.api.views.register import RegisterSigner
from rest_registration.settings import registration_settings
from tests.utils import TestCase, shallow_merge_dicts

from .base import APIViewTestCase

REGISTER_VERIFICATION_URL = '/verify-account/'
VERIFICATION_FROM_EMAIL = 'no-reply@example.com'
REST_REGISTRATION_WITH_VERIFICATION = {
    'REGISTER_VERIFICATION_ENABLED': True,
    'REGISTER_VERIFICATION_URL': REGISTER_VERIFICATION_URL,
    'VERIFICATION_FROM_EMAIL': VERIFICATION_FROM_EMAIL,
}

REST_REGISTRATION_WITHOUT_VERIFICATION = {
    'REGISTER_VERIFICATION_ENABLED': False,
}

REST_REGISTRATION_WITH_HTML_EMAIL_VERIFICATION = {
    'REGISTER_VERIFICATION_ENABLED': True,
    'REGISTER_VERIFICATION_URL': REGISTER_VERIFICATION_URL,
    'REGISTER_VERIFICATION_EMAIL_TEMPLATES': {
        'subject':  'rest_registration/register/subject.txt',
        'html_body':  'rest_registration/register/body.html',
    },
    'VERIFICATION_FROM_EMAIL': VERIFICATION_FROM_EMAIL,
}


@override_settings(REST_REGISTRATION=REST_REGISTRATION_WITH_VERIFICATION)
class RegisterSerializerTestCase(TestCase):

    def test_ok(self):
        serializer_class = registration_settings.REGISTER_SERIALIZER_CLASS
        serializer = serializer_class(data={})
        field_names = set(serializer.get_fields())
        self.assertEqual(
            field_names,
            {'id', 'username', 'first_name', 'last_name', 'email',
             'password', 'password_confirm'},
        )

    @override_settings(
        REST_REGISTRATION=shallow_merge_dicts(
            REST_REGISTRATION_WITH_VERIFICATION, {
                'REGISTER_SERIALIZER_PASSWORD_CONFIRM': False,
            },
        ),
    )
    def test_no_password_ok(self):
        serializer_class = registration_settings.REGISTER_SERIALIZER_CLASS
        serializer = serializer_class(data={})
        field_names = set(serializer.get_fields())
        self.assertEqual(
            field_names,
            {'id', 'username', 'first_name', 'last_name', 'email', 'password'},
        )


@override_settings(REST_REGISTRATION=REST_REGISTRATION_WITH_VERIFICATION)
class RegisterSignerTestCase(TestCase):

    def test_signer_with_different_secret_keys(self):
        user = self.create_test_user(is_active=False)
        data_to_sign = {'user_id': user.pk}
        secrets = [
            '#0ka!t#6%28imjz+2t%l(()yu)tg93-1w%$du0*po)*@l+@+4h',
            'feb7tjud7m=91$^mrk8dq&nz(0^!6+1xk)%gum#oe%(n)8jic7',
        ]
        signatures = []
        for secret in secrets:
            with override_settings(
                    SECRET_KEY=secret):
                signer = RegisterSigner(data_to_sign)
                data = signer.get_signed_data()
                signatures.append(data[signer.SIGNATURE_FIELD])

        assert signatures[0] != signatures[1]


def build_custom_verification_url(signer):
    base_url = signer.get_base_url()
    signed_data = signer.get_signed_data()
    if signer.USE_TIMESTAMP:
        timestamp = signed_data.pop(signer.TIMESTAMP_FIELD)
    else:
        timestamp = None
    signature = signed_data.pop(signer.SIGNATURE_FIELD)
    segments = [signed_data[k] for k in sorted(signed_data.keys())]
    segments.append(signature)
    if timestamp:
        segments.append(timestamp)
    quoted_segments = [urlquote(str(s)) for s in segments]

    url = base_url
    if not url.endswith('/'):
        url += '/'
    url += '/'.join(quoted_segments)
    url += '/'
    if signer.request:
        url = signer.request.build_absolute_uri(url)

    return url


def parse_custom_verification_url(url, verification_field_names):
    parsed_url = urlparse(url)
    num_of_fields = len(verification_field_names)
    url_path = parsed_url.path.rstrip('/')
    url_segments = url_path.rsplit('/', num_of_fields)
    if len(url_segments) != num_of_fields + 1:
        raise ValueError("Could not parse {url}".format(url=url))

    data_segments = url_segments[1:]
    url_path = url_segments[0] + '/'
    verification_data = {
        name: urlunquote(value)
        for name, value in zip(verification_field_names, data_segments)}
    return url_path, verification_data


@override_settings(REST_REGISTRATION=REST_REGISTRATION_WITH_VERIFICATION)
class RegisterViewTestCase(APIViewTestCase):
    VIEW_NAME = 'register'

    def test_register_ok(self):
        data = self._get_register_user_data(password='testpassword')
        request = self.create_post_request(data)
        with self.assert_one_mail_sent() as sent_emails, self.timer() as timer:
            response = self.view_func(request)
            self.assert_valid_response(response, status.HTTP_201_CREATED)
        user_id = response.data['id']
        # Check database state.
        user = self.user_class.objects.get(id=user_id)
        self.assertEqual(user.username, data['username'])
        self.assertTrue(user.check_password(data['password']))
        self.assertFalse(user.is_active)
        # Check verification e-mail.
        sent_email = sent_emails[0]
        self.assertEqual(sent_email.from_email, VERIFICATION_FROM_EMAIL)
        self.assertListEqual(sent_email.to, [data['email']])
        url = self.assert_one_url_line_in_text(sent_email.body)

        verification_data = self.assert_valid_verification_url(
            url,
            expected_path=REGISTER_VERIFICATION_URL,
            expected_fields={'signature', 'user_id', 'timestamp'},
        )
        url_user_id = int(verification_data['user_id'])
        self.assertEqual(url_user_id, user_id)
        url_sig_timestamp = int(verification_data['timestamp'])
        self.assertGreaterEqual(url_sig_timestamp, timer.start_time)
        self.assertLessEqual(url_sig_timestamp, timer.end_time)
        signer = RegisterSigner(verification_data)
        signer.verify()

    @override_settings(
        REST_REGISTRATION=shallow_merge_dicts(
            REST_REGISTRATION_WITH_VERIFICATION, {
                'USER_VERIFICATION_ID_FIELD': 'username',
            },
        ),
    )
    def test_register_with_username_as_verification_id_ok(self):
        # Using username is not recommended if it can change for a given user.
        data = self._get_register_user_data(password='testpassword')
        request = self.create_post_request(data)
        with self.assert_one_mail_sent() as sent_emails, self.timer() as timer:
            response = self.view_func(request)
            self.assert_valid_response(response, status.HTTP_201_CREATED)
        user_id = response.data['id']
        # Check database state.
        user = self.user_class.objects.get(id=user_id)
        self.assertEqual(user.username, data['username'])
        self.assertTrue(user.check_password(data['password']))
        self.assertFalse(user.is_active)
        # Check verification e-mail.
        sent_email = sent_emails[0]
        self.assertEqual(sent_email.from_email, VERIFICATION_FROM_EMAIL)
        self.assertListEqual(sent_email.to, [data['email']])
        url = self.assert_one_url_line_in_text(sent_email.body)

        verification_data = self.assert_valid_verification_url(
            url,
            expected_path=REGISTER_VERIFICATION_URL,
            expected_fields={'signature', 'user_id', 'timestamp'},
        )
        user_verification_id = verification_data['user_id']
        self.assertEqual(user_verification_id, user.username)
        url_sig_timestamp = int(verification_data['timestamp'])
        self.assertGreaterEqual(url_sig_timestamp, timer.start_time)
        self.assertLessEqual(url_sig_timestamp, timer.end_time)
        signer = RegisterSigner(verification_data)
        signer.verify()

    @override_settings(
        REST_REGISTRATION=shallow_merge_dicts(
            REST_REGISTRATION_WITH_VERIFICATION, {
                'VERIFICATION_URL_BUILDER': build_custom_verification_url,
            },
        ),
    )
    def test_register_with_custom_verification_url_ok(self):
        data = self._get_register_user_data(password='testpassword')
        request = self.create_post_request(data)
        with self.assert_one_mail_sent() as sent_emails, self.timer() as timer:
            response = self.view_func(request)
            self.assert_valid_response(response, status.HTTP_201_CREATED)
        user_id = response.data['id']
        # Check database state.
        user = self.user_class.objects.get(id=user_id)
        self.assertEqual(user.username, data['username'])
        self.assertTrue(user.check_password(data['password']))
        self.assertFalse(user.is_active)
        # Check verification e-mail.
        sent_email = sent_emails[0]
        self.assertEqual(sent_email.from_email, VERIFICATION_FROM_EMAIL)
        self.assertListEqual(sent_email.to, [data['email']])
        url = self.assert_one_url_line_in_text(sent_email.body)

        verification_data = self.assert_valid_verification_url(
            url,
            expected_path=REGISTER_VERIFICATION_URL,
            expected_fields=['user_id', 'signature', 'timestamp'],
            url_parser=parse_custom_verification_url,
        )
        url_user_id = int(verification_data['user_id'])
        self.assertEqual(url_user_id, user_id)
        url_sig_timestamp = int(verification_data['timestamp'])
        self.assertGreaterEqual(url_sig_timestamp, timer.start_time)
        self.assertLessEqual(url_sig_timestamp, timer.end_time)
        signer = RegisterSigner(verification_data)
        signer.verify()

    @override_settings(
        REST_REGISTRATION=REST_REGISTRATION_WITH_HTML_EMAIL_VERIFICATION,
    )
    def test_register_with_html_email_ok(self):
        data = self._get_register_user_data(password='testpassword')
        request = self.create_post_request(data)
        with self.assert_one_mail_sent() as sent_emails, self.timer() as timer:
            response = self.view_func(request)
            self.assert_valid_response(response, status.HTTP_201_CREATED)
        user_id = response.data['id']
        # Check database state.
        user = self.user_class.objects.get(id=user_id)
        self.assertEqual(user.username, data['username'])
        self.assertTrue(user.check_password(data['password']))
        self.assertFalse(user.is_active)
        # Check verification e-mail.
        sent_email = sent_emails[0]
        self.assertEqual(sent_email.from_email, VERIFICATION_FROM_EMAIL)
        self.assertListEqual(sent_email.to, [data['email']])
        url = self.assert_one_url_in_brackets_in_text(sent_email.body)

        verification_data = self.assert_valid_verification_url(
            url,
            expected_path=REGISTER_VERIFICATION_URL,
            expected_fields={'signature', 'user_id', 'timestamp'},
        )
        url_user_id = int(verification_data['user_id'])
        self.assertEqual(url_user_id, user_id)
        url_sig_timestamp = int(verification_data['timestamp'])
        self.assertGreaterEqual(url_sig_timestamp, timer.start_time)
        self.assertLessEqual(url_sig_timestamp, timer.end_time)
        signer = RegisterSigner(verification_data)
        signer.verify()

    @override_settings(
        REST_REGISTRATION=shallow_merge_dicts(
            REST_REGISTRATION_WITH_VERIFICATION, {
                'REGISTER_SERIALIZER_PASSWORD_CONFIRM': False,
            },
        ),
    )
    def test_register_no_password_confirm_ok(self):
        data = self._get_register_user_data(password='testpassword')
        data.pop('password_confirm')
        request = self.create_post_request(data)
        with self.assert_one_mail_sent() as sent_emails, self.timer() as timer:
            response = self.view_func(request)
            self.assert_valid_response(response, status.HTTP_201_CREATED)
        user_id = response.data['id']
        # Check database state.
        user = self.user_class.objects.get(id=user_id)
        self.assertEqual(user.username, data['username'])
        self.assertTrue(user.check_password(data['password']))
        self.assertFalse(user.is_active)
        # Check verification e-mail.
        sent_email = sent_emails[0]
        self.assertEqual(sent_email.from_email, VERIFICATION_FROM_EMAIL)
        self.assertListEqual(sent_email.to, [data['email']])
        url = self.assert_one_url_line_in_text(sent_email.body)

        verification_data = self.assert_valid_verification_url(
            url,
            expected_path=REGISTER_VERIFICATION_URL,
            expected_fields={'signature', 'user_id', 'timestamp'},
        )
        url_user_id = int(verification_data['user_id'])
        self.assertEqual(url_user_id, user_id)
        url_sig_timestamp = int(verification_data['timestamp'])
        self.assertGreaterEqual(url_sig_timestamp, timer.start_time)
        self.assertLessEqual(url_sig_timestamp, timer.end_time)
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

    @override_settings(
        EMAIL_BACKEND='tests.api.test_register.FailureEmailBackend',
    )
    def test_when_notification_failure_then_user_not_created(self):
        data = self._get_register_user_data(password='testpassword')
        request = self.create_post_request(data)
        user_ids_before = {u.pk for u in self.user_class.objects.all()}
        with self.capture_sent_emails() as sent_emails, \
                pytest.raises(ConnectionRefusedError):
            self.view_func(request)
        self.assert_len_equals(sent_emails, 0)
        user_ids_after = {u.pk for u in self.user_class.objects.all()}
        self.assertSetEqual(user_ids_after, user_ids_before)

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

    @override_settings(REST_REGISTRATION=REST_REGISTRATION_WITH_VERIFICATION)
    def test_verify_ok(self):
        user, request = self.prepare_user_and_request()
        response = self.view_func(request)
        self.assert_valid_response(response, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    @override_settings(
        REST_REGISTRATION=shallow_merge_dicts(
            REST_REGISTRATION_WITH_VERIFICATION, {
                'USER_VERIFICATION_ID_FIELD': 'username',
            },
        ),
    )
    def test_verify_with_username_as_verification_id_ok(self):
        user = self.prepare_user()
        request = self.prepare_request(
            user, data_to_sign={'user_id': user.username})
        response = self.view_func(request)
        self.assert_valid_response(response, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    @override_settings(REST_REGISTRATION=REST_REGISTRATION_WITH_VERIFICATION)
    def test_verify_ok_idempotent(self):
        user = self.prepare_user()
        request1 = self.prepare_request(user)
        request2 = self.prepare_request(user)

        self.view_func(request1)

        response = self.view_func(request2)
        self.assert_valid_response(response, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    @override_settings(
        REST_REGISTRATION=shallow_merge_dicts(
            REST_REGISTRATION_WITH_VERIFICATION, {
                'REGISTER_VERIFICATION_ONE_TIME_USE': True,
            },
        ),
    )
    def test_verify_one_time_use(self):
        user = self.prepare_user()
        request1 = self.prepare_request(user)
        request2 = self.prepare_request(user)

        self.view_func(request1)

        response = self.view_func(request2)
        self.assert_valid_response(response, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    @override_settings(
        REST_REGISTRATION=shallow_merge_dicts(
            REST_REGISTRATION_WITH_VERIFICATION, {
                'REGISTER_VERIFICATION_AUTO_LOGIN': True,
            },
        ),
    )
    def test_verify_ok_login(self):
        with patch('django.contrib.auth.login') as login_mock:
            user, request = self.prepare_user_and_request()
            response = self.view_func(request)
            login_mock.assert_called_once_with(mock.ANY, user)
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
        user, request = self.prepare_user_and_request()
        response = self.view_func(request)

        self.assert_invalid_response(response, status.HTTP_404_NOT_FOUND)
        user.refresh_from_db()
        self.assertFalse(user.is_active)


class FailureEmailBackend(BaseEmailBackend):

    def send_messages(self, email_messages):
        if not email_messages:
            return
        raise ConnectionRefusedError()

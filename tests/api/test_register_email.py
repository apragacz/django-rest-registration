import time
from unittest.mock import patch

from django.conf import settings
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.test import force_authenticate

from rest_registration.api.views.register_email import RegisterEmailSigner
from tests.utils import TestCase, shallow_merge_dicts

from .base import APIViewTestCase

REGISTER_EMAIL_VERIFICATION_URL = '/verify-email/'
REST_REGISTRATION_WITH_EMAIL_VERIFICATION = {
    'REGISTER_EMAIL_VERIFICATION_ENABLED': True,
    'REGISTER_EMAIL_VERIFICATION_URL': REGISTER_EMAIL_VERIFICATION_URL,
    'VERIFICATION_FROM_EMAIL': 'no-reply@example.com',
}


@override_settings(REST_REGISTRATION=REST_REGISTRATION_WITH_EMAIL_VERIFICATION)
class RegisterEmailSignerTestCase(TestCase):

    def test_signer_with_different_secret_keys(self):
        email = 'testuser1@example.com'
        user = self.create_test_user(is_active=False)
        data_to_sign = {
            'user_id': user.pk,
            'email': email,
        }
        secrets = [
            '#0ka!t#6%28imjz+2t%l(()yu)tg93-1w%$du0*po)*@l+@+4h',
            'feb7tjud7m=91$^mrk8dq&nz(0^!6+1xk)%gum#oe%(n)8jic7',
        ]
        signatures = []
        for secret in secrets:
            with override_settings(
                    SECRET_KEY=secret):
                signer = RegisterEmailSigner(data_to_sign)
                data = signer.get_signed_data()
                signatures.append(data[signer.SIGNATURE_FIELD])

        assert signatures[0] != signatures[1]


class BaseRegisterEmailViewTestCase(APIViewTestCase):

    def setUp(self):
        super().setUp()
        self.email = 'testuser1@example.com'
        self.new_email = 'testuser2@example.com'
        self.user = None
        self.user2 = None

    def create_authenticated_post_request(self, data):
        request = self.create_post_request(data)
        force_authenticate(request, user=self.user)
        return request

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

    def assert_valid_verification_email_sent(self, sent_emails, timer=None):
        self.assert_len_equals(sent_emails, 1)
        sent_email = sent_emails[0]
        self.assertEqual(
            sent_email.from_email,
            settings.REST_REGISTRATION['VERIFICATION_FROM_EMAIL'],
        )
        self.assertListEqual(sent_email.to, [self.new_email])
        url = self.assert_one_url_line_in_text(sent_email.body)
        verification_data = self.assert_valid_verification_url(
            url,
            expected_path=settings.REST_REGISTRATION['REGISTER_EMAIL_VERIFICATION_URL'],  # noqa: E501
            expected_fields={'signature', 'user_id', 'timestamp', 'email'},
        )
        self.assertEqual(verification_data['email'], self.new_email)
        self.assertEqual(int(verification_data['user_id']), self.user.id)
        url_sig_timestamp = int(verification_data['timestamp'])
        if timer:
            self.assertGreaterEqual(url_sig_timestamp, timer.start_time)
            self.assertLessEqual(url_sig_timestamp, timer.end_time)
        signer = RegisterEmailSigner(verification_data)
        signer.verify()

    def assert_notification_already_exists_sent(self, sent_emails):
        self.assert_len_equals(sent_emails, 1)
        sent_email = sent_emails[0]
        self.assertEqual(
            sent_email.from_email,
            settings.REST_REGISTRATION['VERIFICATION_FROM_EMAIL'],
        )
        self.assertListEqual(sent_email.to, [self.new_email])
        self.assertIn("already in use", sent_email.subject)
        self.assertIn(
            "this e-mail for which there is an existing account",
            sent_email.body,
        )
        self.assert_no_url_in_text(sent_email.body)


class RegisterEmailViewTestCase(BaseRegisterEmailViewTestCase):
    VIEW_NAME = 'register-email'

    def _test_authenticated(self, data):
        request = self.create_authenticated_post_request(data)
        response = self.view_func(request)
        return response

    @override_settings(
        REST_REGISTRATION=REST_REGISTRATION_WITH_EMAIL_VERIFICATION,
    )
    def test_ok(self):
        self.setup_user()
        data = {
            'email': self.new_email,
        }
        with self.assert_one_mail_sent() as sent_emails, self.timer() as timer:
            response = self._test_authenticated(data)
            self.assert_valid_response(response, status.HTTP_200_OK)
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
            expected_fields={'signature', 'user_id', 'timestamp', 'email'},
        )
        self.assertEqual(verification_data['email'], self.new_email)
        self.assertEqual(int(verification_data['user_id']), self.user.id)
        url_sig_timestamp = int(verification_data['timestamp'])
        self.assertGreaterEqual(url_sig_timestamp, timer.start_time)
        self.assertLessEqual(url_sig_timestamp, timer.end_time)
        signer = RegisterEmailSigner(verification_data)
        signer.verify()

    @override_settings(
        REST_REGISTRATION=REST_REGISTRATION_WITH_EMAIL_VERIFICATION,
    )
    def test_email_already_in_use_ok(self):
        self.setup_user()
        self.setup_user2_with_user_new_email()
        request = self.create_authenticated_post_request({
            'email': self.new_email,
        })
        with self.capture_sent_emails() as sent_emails, self.timer() as timer:
            response = self.view_func(request)
        self.assert_response_is_ok(response)
        self.assert_user_email_not_changed()
        self.assert_valid_verification_email_sent(sent_emails, timer=timer)

    @override_settings(
        AUTH_USER_MODEL='custom_users.UserWithUniqueEmail',
        REST_REGISTRATION=REST_REGISTRATION_WITH_EMAIL_VERIFICATION,
    )
    def test_user_with_unique_email_ok_but_notification_already_exists(self):
        self.setup_user()
        self.setup_user2_with_user_new_email()
        request = self.create_authenticated_post_request({
            'email': self.new_email,
        })
        with self.capture_sent_emails() as sent_emails:
            response = self.view_func(request)
        self.assert_response_is_ok(response)
        self.assert_user_email_not_changed()
        self.assert_notification_already_exists_sent(sent_emails)

    @override_settings(
        REST_REGISTRATION=shallow_merge_dicts(
            REST_REGISTRATION_WITH_EMAIL_VERIFICATION, {
                'USER_VERIFICATION_ID_FIELD': 'username',
            },
        ),
    )
    def test_with_username_as_verification_id_ok(self):
        self.setup_user()
        data = {
            'email': self.new_email,
        }
        with self.assert_one_mail_sent() as sent_emails, self.timer() as timer:
            response = self._test_authenticated(data)
            self.assert_valid_response(response, status.HTTP_200_OK)
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
            expected_fields={'signature', 'user_id', 'timestamp', 'email'},
        )
        self.assertEqual(verification_data['email'], self.new_email)
        self.assertEqual(verification_data['user_id'], self.user.username)
        url_sig_timestamp = int(verification_data['timestamp'])
        self.assertGreaterEqual(url_sig_timestamp, timer.start_time)
        self.assertLessEqual(url_sig_timestamp, timer.end_time)
        signer = RegisterEmailSigner(verification_data)
        signer.verify()

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_EMAIL_VERIFICATION_ENABLED': False
        }
    )
    def test_noverify_ok(self):
        self.setup_user()
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
        REST_REGISTRATION=REST_REGISTRATION_WITH_EMAIL_VERIFICATION,
    )
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

    @override_settings(
        REST_REGISTRATION=REST_REGISTRATION_WITH_EMAIL_VERIFICATION,
    )
    def test_new_email_already_in_use_ok(self):
        self.setup_user()
        self.setup_user2_with_user_new_email()
        signer = self.build_signer()
        request = self.create_post_request(signer.get_signed_data())
        response = self.view_func(request)
        self.assert_response_is_ok(response)
        self.assert_user_email_changed()

    @override_settings(
        REST_REGISTRATION=shallow_merge_dicts(
            REST_REGISTRATION_WITH_EMAIL_VERIFICATION, {
                'USER_VERIFICATION_ID_FIELD': 'username',
            },
        ),
    )
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
        self.assert_response_is_not_found(response)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, old_email)

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
        }
    )
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

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_EMAIL_VERIFICATION_URL': REGISTER_EMAIL_VERIFICATION_URL,
        }
    )
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

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_EMAIL_VERIFICATION_URL': REGISTER_EMAIL_VERIFICATION_URL,
        }
    )
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

    @override_settings(
        REST_REGISTRATION={
            'REGISTER_EMAIL_VERIFICATION_URL': REGISTER_EMAIL_VERIFICATION_URL,
        }
    )
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

    @override_settings(
        AUTH_USER_MODEL='custom_users.UserWithUniqueEmail',
        REST_REGISTRATION=REST_REGISTRATION_WITH_EMAIL_VERIFICATION,
    )
    def test_user_with_unique_email_user_email_already_exists(self):
        self.setup_user()
        self.setup_user2_with_user_new_email()
        signer = self.build_signer()
        request = self.create_post_request(signer.get_signed_data())
        response = self.view_func(request)
        self.assert_response_is_bad_request(response)
        self.assert_user_email_not_changed()

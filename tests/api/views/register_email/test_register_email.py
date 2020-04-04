from django.conf import settings
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.test import force_authenticate

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
class RegisterEmailViewTestCase(APIViewTestCase):
    VIEW_NAME = 'register-email'

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

    def _test_authenticated(self, data):
        request = self.create_authenticated_post_request(data)
        response = self.view_func(request)
        return response

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
        self.assertEqual(sent_email.from_email, VERIFICATION_FROM_EMAIL)
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

    @override_auth_model_settings('custom_users.UserWithUniqueEmail')
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

    @override_rest_registration_settings({
        'USER_VERIFICATION_ID_FIELD': 'username',
    })
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
        self.assertEqual(sent_email.from_email, VERIFICATION_FROM_EMAIL)
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

    @override_rest_registration_settings({
        'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
    })
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

    @override_settings(
        TEMPLATES=(),
    )
    @override_rest_registration_settings({
        'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
    })
    def test_no_templates_without_verification_ok(self):
        self.setup_user()
        with self.capture_sent_emails() as sent_emails:
            response = self._test_authenticated({
                'email': self.new_email,
            })
        self.assert_response_is_ok(response)
        self.assert_len_equals(sent_emails, 0)
        self.assert_user_email_changed()

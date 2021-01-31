from unittest import skip

import pytest
from django.test.utils import override_settings
from rest_framework import status

from rest_registration.api.views.reset_password import ResetPasswordSigner
from tests.helpers.api_views import assert_response_is_ok
from tests.helpers.constants import (
    RESET_PASSWORD_VERIFICATION_URL,
    VERIFICATION_FROM_EMAIL
)
from tests.helpers.email import (
    assert_no_email_sent,
    assert_one_email_sent,
    capture_sent_emails
)
from tests.helpers.settings import override_rest_registration_settings
from tests.helpers.text import assert_one_url_line_in_text
from tests.helpers.timer import capture_time
from tests.helpers.verification import assert_valid_verification_url
from tests.helpers.views import ViewProvider

from ..base import APIViewTestCase


@override_rest_registration_settings({
    'RESET_PASSWORD_VERIFICATION_ENABLED': True,
    'RESET_PASSWORD_VERIFICATION_URL': RESET_PASSWORD_VERIFICATION_URL,
    'VERIFICATION_FROM_EMAIL': VERIFICATION_FROM_EMAIL,
})
class SendResetPasswordLinkViewTestCase(APIViewTestCase):
    VIEW_NAME = 'send-reset-password-link'

    def test_send_link_ok(self):
        user = self.create_test_user(username='testusername')
        request = self.create_post_request({
            'login': user.username,
        })
        with self.assert_one_mail_sent() as sent_emails, self.timer() as timer:
            response = self.view_func(request)
            self.assert_valid_response(response, status.HTTP_200_OK)
        sent_email = sent_emails[0]
        self._assert_valid_send_link_email(sent_email, user, timer)

    @override_rest_registration_settings({
        'USER_VERIFICATION_ID_FIELD': 'username',
    })
    def test_send_link_with_username_as_verification_id_ok(self):
        user = self.create_test_user(username='testusername')
        request = self.create_post_request({
            'login': user.username,
        })
        with self.assert_one_mail_sent() as sent_emails, self.timer() as timer:
            response = self.view_func(request)
            self.assert_valid_response(response, status.HTTP_200_OK)
        sent_email = sent_emails[0]
        verification_data = self._assert_valid_verification_email(
            sent_email, user)
        self.assertEqual(verification_data['user_id'], user.username)
        url_sig_timestamp = int(verification_data['timestamp'])
        self.assertGreaterEqual(url_sig_timestamp, timer.start_time)
        self.assertLessEqual(url_sig_timestamp, timer.end_time)
        signer = ResetPasswordSigner(verification_data)
        signer.verify()

    def test_send_link_but_email_not_in_login_fields(self):
        user = self.create_test_user(
            username='testusername', email='testuser@example.com')
        request = self.create_post_request({
            'login': user.email,
        })
        with self.assert_no_mail_sent():
            response = self.view_func(request)
            self.assert_response_is_bad_request(response)

    @override_rest_registration_settings({
        'USER_LOGIN_FIELDS': ['username', 'email'],
    })
    def test_send_link_via_login_username_ok(self):
        user = self.create_test_user(username='testusername')
        request = self.create_post_request({
            'login': user.username,
        })
        with self.assert_one_mail_sent() as sent_emails, self.timer() as timer:
            response = self.view_func(request)
            self.assert_valid_response(response, status.HTTP_200_OK)
        sent_email = sent_emails[0]
        self._assert_valid_send_link_email(sent_email, user, timer)

    @override_rest_registration_settings({
        'USER_LOGIN_FIELDS': ['username', 'email'],
    })
    def test_send_link_via_login_email_ok(self):
        user = self.create_test_user(
            username='testusername', email='testuser@example.com')
        request = self.create_post_request({
            'login': user.email,
        })
        with self.assert_one_mail_sent() as sent_emails, self.timer() as timer:
            response = self.view_func(request)
            self.assert_valid_response(response, status.HTTP_200_OK)
        sent_email = sent_emails[0]
        self._assert_valid_send_link_email(sent_email, user, timer)

    @override_rest_registration_settings({
        'USER_LOGIN_FIELDS': ['username', 'email'],
        'SEND_RESET_PASSWORD_LINK_SERIALIZER_USE_EMAIL': True,
    })
    def test_send_link_via_email_ok(self):
        user = self.create_test_user(
            username='testusername', email='testuser@example.com')
        request = self.create_post_request({
            'email': user.email,
        })
        with self.assert_one_mail_sent() as sent_emails, self.timer() as timer:
            response = self.view_func(request)
            self.assert_valid_response(response, status.HTTP_200_OK)
        sent_email = sent_emails[0]
        self._assert_valid_send_link_email(sent_email, user, timer)

    @skip("TODO: Issue #35")
    def test_send_link_disabled_user(self):
        pass

    def test_send_link_unverified_user(self):
        user = self.create_test_user(username='testusername', is_active=False)
        request = self.create_post_request({
            'login': user.username,
        })
        with self.assert_one_mail_sent() as sent_emails, self.timer() as timer:
            response = self.view_func(request)
            self.assert_valid_response(response, status.HTTP_200_OK)
        sent_email = sent_emails[0]
        self._assert_valid_send_link_email(sent_email, user, timer)

    @override_rest_registration_settings({
        'RESET_PASSWORD_VERIFICATION_ONE_TIME_USE': True,
    })
    def test_send_link_unverified_user_one_time_use(self):
        user = self.create_test_user(username='testusername', is_active=False)
        request = self.create_post_request({
            'login': user.username,
        })
        with self.assert_one_mail_sent() as sent_emails, self.timer() as timer:
            response = self.view_func(request)
            self.assert_valid_response(response, status.HTTP_200_OK)
        sent_email = sent_emails[0]
        self._assert_valid_send_link_email(sent_email, user, timer)

    @override_rest_registration_settings({
        'RESET_PASSWORD_VERIFICATION_ENABLED': False,
    })
    def test_reset_password_disabled(self):
        user = self.create_test_user(username='testusername')
        request = self.create_post_request({
            'login': user.username,
        })
        with self.assert_no_mail_sent():
            response = self.view_func(request)
            self.assert_response_is_not_found(response)

    @override_rest_registration_settings({
        'RESET_PASSWORD_VERIFICATION_ENABLED': False,
    })
    @override_settings(
        TEMPLATES=(),
    )
    def test_no_templates_reset_password_disabled(self):
        user = self.create_test_user(username='testusername')
        request = self.create_post_request({
            'login': user.username,
        })
        with capture_sent_emails() as sent_emails:
            response = self.view_func(request)
        self.assert_response_is_not_found(response)
        self.assert_len_equals(sent_emails, 0)

    def test_send_link_invalid_login(self):
        user = self.create_test_user(username='testusername')
        request = self.create_post_request({
            'login': user.username + 'b',
        })
        with self.assert_mails_sent(0):
            response = self.view_func(request)
            self.assert_response_is_bad_request(response)

    def _assert_valid_send_link_email(self, sent_email, user, timer):
        verification_data = self._assert_valid_verification_email(
            sent_email, user)
        self._assert_valid_verification_data(verification_data, user, timer)

    def _assert_valid_verification_email(self, sent_email, user):
        self.assertEqual(
            sent_email.from_email,
            VERIFICATION_FROM_EMAIL,
        )
        self.assertListEqual(sent_email.to, [user.email])
        url = self.assert_one_url_line_in_text(sent_email.body)
        verification_data = self.assert_valid_verification_url(
            url,
            expected_path=RESET_PASSWORD_VERIFICATION_URL,
            expected_fields={'signature', 'user_id', 'timestamp'},
        )
        return verification_data

    def _assert_valid_verification_data(self, verification_data, user, timer):
        self.assertEqual(int(verification_data['user_id']), user.id)
        url_sig_timestamp = int(verification_data['timestamp'])
        self.assertGreaterEqual(url_sig_timestamp, timer.start_time)
        self.assertLessEqual(url_sig_timestamp, timer.end_time)
        signer = ResetPasswordSigner(verification_data)
        signer.verify()


@pytest.fixture()
def api_view_provider():
    return ViewProvider('send-reset-password-link')


def test_when_duplicated_email_then_send_link_via_login_successful(
        settings_with_reset_password_verification,
        api_view_provider, api_factory,
        user, user2_with_user_email):
    request = api_factory.create_post_request({
        'login': user.username,
    })
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_one_email_sent(sent_emails)

    sent_email = sent_emails[0]
    assert_valid_send_link_email(sent_email, user, timer)


def test_when_no_user_reveal_then_send_link_successful(
        settings_with_reset_password_verification,
        settings_with_reset_password_fail_when_user_not_found_disabled,
        api_view_provider, api_factory,
        user):
    request = api_factory.create_post_request({
        'login': user.username,
    })
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_one_email_sent(sent_emails)

    sent_email = sent_emails[0]
    assert_valid_send_link_email(sent_email, user, timer)


@pytest.mark.django_db
def test_when_no_user_reveal_and_user_not_found_then_send_link_successful(
        settings_with_reset_password_verification,
        settings_with_reset_password_fail_when_user_not_found_disabled,
        api_view_provider, api_factory):
    request = api_factory.create_post_request({
        'login': 'ninja',
    })
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_no_email_sent(sent_emails)


@override_rest_registration_settings({
    'SEND_RESET_PASSWORD_LINK_SERIALIZER_CLASS': 'tests.testapps.custom_serializers.serializers.DefaultDeprecatedSendResetPasswordLinkSerializer',  # noqa: E501
})
def test_when_deprecated_send_reset_password_link_serializer_then_success(
        settings_with_reset_password_verification, user,
        api_view_provider, api_factory):
    request = api_factory.create_post_request({
        'login': 'abra',
    })
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)


def assert_valid_send_link_email(sent_email, user, timer):
    verification_data = _assert_valid_reset_password_verification_email(
        sent_email, user)
    _assert_valid_reset_password_verification_data(
        verification_data, user, timer)


def _assert_valid_reset_password_verification_email(sent_email, user):
    assert sent_email.from_email == VERIFICATION_FROM_EMAIL
    assert sent_email.to == [user.email]
    url = assert_one_url_line_in_text(sent_email.body)
    verification_data = assert_valid_verification_url(
        url,
        expected_path=RESET_PASSWORD_VERIFICATION_URL,
        expected_fields={'signature', 'user_id', 'timestamp'},
    )
    return verification_data


def _assert_valid_reset_password_verification_data(
        verification_data, user, timer):
    assert int(verification_data['user_id']) == user.id
    url_sig_timestamp = int(verification_data['timestamp'])
    assert url_sig_timestamp >= timer.start_time
    assert url_sig_timestamp <= timer.end_time
    signer = ResetPasswordSigner(verification_data)
    signer.verify()

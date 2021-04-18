from unittest import mock

import pytest
from django.conf import settings
from django.core import signing
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.test import force_authenticate

from rest_registration.api.views.register_email import RegisterEmailSigner
from rest_registration.exceptions import SignatureExpired, SignatureInvalid
from rest_registration.utils.verification import verify_signer_or_bad_request
from tests.helpers.api_views import (
    assert_response_is_bad_request,
    assert_response_is_ok
)
from tests.helpers.constants import (
    REGISTER_EMAIL_VERIFICATION_URL,
    VERIFICATION_FROM_EMAIL
)
from tests.helpers.email import (
    assert_no_email_sent,
    assert_one_email_sent,
    capture_sent_emails
)
from tests.helpers.settings import (
    override_auth_model_settings,
    override_rest_registration_settings
)
from tests.helpers.text import assert_one_url_line_in_text
from tests.helpers.timer import capture_time
from tests.helpers.verification import assert_valid_verification_url
from tests.helpers.views import ViewProvider

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


@override_rest_registration_settings({
    'USE_NON_FIELD_ERRORS_KEY_FROM_DRF_SETTINGS': True
})
@pytest.mark.parametrize("exception,expected", (
    (signing.SignatureExpired, SignatureExpired),
    (signing.BadSignature, SignatureInvalid))
                         )
def test_verify_signer_or_bad_request_non_field_errors(exception, expected):
    # arrange
    mock_signer = mock.MagicMock()
    mock_verify = mock.Mock(side_effect=exception())
    mock_signer.verify = mock_verify

    # act, assert
    with pytest.raises(expected) as context:
        verify_signer_or_bad_request(mock_signer)

    assert 'non_field_errors' in context.value.get_full_details()


@override_rest_registration_settings({
    'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
    'USE_NON_FIELD_ERRORS_KEY_FROM_DRF_SETTINGS': True,
})
def test_register_email_fail_with_non_field_errors(
        settings_with_simple_email_based_user,
        user,
        api_view_provider, api_factory):
    request = api_factory.create_post_request({
        'email': user.email,
    })
    force_authenticate(request, user=user)
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_no_email_sent(sent_emails)
    assert_response_is_bad_request(response)
    assert "non_field_errors" in response.data


@override_rest_registration_settings({
    'REGISTER_EMAIL_VERIFICATION_ENABLED': False
})
def test_register_email_fail_email_already_used(
        settings_with_simple_email_based_user,
        user,
        api_view_provider, api_factory):
    request = api_factory.create_post_request({
        'email': user.email,
    })
    force_authenticate(request, user=user)
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_no_email_sent(sent_emails)
    assert_response_is_bad_request(response)
    assert "detail" in response.data


@override_rest_registration_settings({
    'REGISTER_EMAIL_SERIALIZER_CLASS': 'tests.testapps.custom_serializers.serializers.DefaultDeprecatedRegisterEmailSerializer',  # noqa: E501
})
def test_ok_when_deprecated_register_email_serializer(
        user,
        api_view_provider, api_factory):
    request = api_factory.create_post_request({
        'email': 'not@used.com',
    })
    force_authenticate(request, user=user)
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_no_email_sent(sent_emails)
    user.refresh_from_db()
    assert user.email == 'abra@cadabra.com'


@override_rest_registration_settings({
    'VERIFICATION_TEMPLATES_SELECTOR': 'tests.testapps.custom_templates.utils.select_verification_templates',  # noqa E501
})
def test_ok_when_custom_verification_templates_selector(
        settings_with_register_email_verification,
        user, email_change,
        api_view_provider, api_factory):
    new_email = email_change.new_value
    request = api_factory.create_post_request({
        'email': new_email,
    })
    force_authenticate(request, user=user)
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_one_email_sent(sent_emails)
    sent_email = sent_emails[0]
    assert sent_email.subject == "Generic verification link was sent"
    assert sent_email.body.startswith("Click URL to verify:")
    assert_valid_register_email_verification_email(sent_email, user, new_email, timer)
    user.refresh_from_db()
    assert user.email == email_change.old_value


@pytest.fixture()
def api_view_provider():
    return ViewProvider('register-email')


def assert_valid_register_email_verification_email(sent_email, user, new_email, timer):
    assert sent_email.from_email == VERIFICATION_FROM_EMAIL
    assert sent_email.to == [new_email]
    url = assert_one_url_line_in_text(sent_email.body)

    verification_data = assert_valid_verification_url(
        url,
        expected_path=REGISTER_EMAIL_VERIFICATION_URL,
        expected_fields={'signature', 'user_id', 'timestamp', 'email'},
        timer=timer,
        signer_cls=RegisterEmailSigner,
    )
    url_user_id = int(verification_data['user_id'])
    assert url_user_id == user.pk

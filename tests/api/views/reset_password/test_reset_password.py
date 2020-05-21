import time
from unittest import skip
from unittest.mock import patch

import pytest
from rest_framework import status

from rest_registration.api.views.reset_password import ResetPasswordSigner
from tests.helpers.api_views import (
    assert_response_is_bad_request,
    assert_response_is_ok
)
from tests.helpers.constants import (
    RESET_PASSWORD_VERIFICATION_URL,
    VERIFICATION_FROM_EMAIL
)
from tests.helpers.settings import override_rest_registration_settings
from tests.helpers.views import ViewProvider

from ..base import APIViewTestCase

REST_REGISTRATION_WITH_RESET_PASSWORD = {
    'RESET_PASSWORD_VERIFICATION_URL': RESET_PASSWORD_VERIFICATION_URL,
    'VERIFICATION_FROM_EMAIL': VERIFICATION_FROM_EMAIL,
}


@override_rest_registration_settings({
    'RESET_PASSWORD_VERIFICATION_ENABLED': True,
    'RESET_PASSWORD_VERIFICATION_URL': RESET_PASSWORD_VERIFICATION_URL,
    'VERIFICATION_FROM_EMAIL': VERIFICATION_FROM_EMAIL,
})
class ResetPasswordViewTestCase(APIViewTestCase):
    VIEW_NAME = 'reset-password'

    def test_reset_ok(self):
        old_password = 'password1'
        new_password = 'eaWrivtig5'
        user = self.create_test_user(password=old_password)
        signer = ResetPasswordSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        data['password'] = new_password
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_response_is_ok(response)
        user.refresh_from_db()
        self.assertTrue(user.check_password(new_password))

    @override_rest_registration_settings({
        'USER_VERIFICATION_ID_FIELD': 'username',
    })
    def test_reset_with_username_as_verification_id_ok(self):
        old_password = 'password1'
        new_password = 'eaWrivtig5'
        user = self.create_test_user(password=old_password)
        signer = ResetPasswordSigner({'user_id': user.username})
        data = signer.get_signed_data()
        data['password'] = new_password
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_response_is_ok(response)
        user.refresh_from_db()
        self.assertTrue(user.check_password(new_password))

    def test_reset_twice_ok(self):
        old_password = 'password1'
        new_first_password = 'eaWrivtig5'
        new_second_password = 'eaWrivtig5'
        user = self.create_test_user(password=old_password)
        signer = ResetPasswordSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        data['password'] = new_first_password
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_response_is_ok(response)
        user.refresh_from_db()
        self.assertTrue(user.check_password(new_first_password))
        data['password'] = new_second_password
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_response_is_ok(response)
        user.refresh_from_db()
        self.assertTrue(user.check_password(new_second_password))

    @override_rest_registration_settings({
        'RESET_PASSWORD_VERIFICATION_ONE_TIME_USE': True,
    })
    def test_one_time_reset_twice_fail(self):
        old_password = 'password1'
        new_first_password = 'eaWrivtig5'
        new_second_password = 'eaWrivtig5'
        user = self.create_test_user(password=old_password)
        signer = ResetPasswordSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        data['password'] = new_first_password
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_response_is_ok(response)
        user.refresh_from_db()
        self.assertTrue(user.check_password(new_first_password))
        data['password'] = new_second_password
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_response_is_bad_request(response)
        user.refresh_from_db()
        self.assertTrue(user.check_password(new_first_password))

    @override_rest_registration_settings({
        'RESET_PASSWORD_VERIFICATION_ENABLED': False,
    })
    def test_reset_password_disabled(self):
        old_password = 'password1'
        new_password = 'eaWrivtig5'
        user = self.create_test_user(password=old_password)
        signer = ResetPasswordSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        data['password'] = new_password
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_response_is_not_found(response)
        user.refresh_from_db()
        self.assertTrue(user.check_password(old_password))

    @skip("TODO: Issue #35")
    def test_reset_disabled_user(self):
        pass

    def test_reset_unverified_user(self):
        old_password = 'password1'
        new_password = 'eaWrivtig5'
        user = self.create_test_user(password=old_password, is_active=False)
        signer = ResetPasswordSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        data['password'] = new_password
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_response_is_ok(response)
        user.refresh_from_db()
        self.assertTrue(user.check_password(new_password))

    def test_reset_tampered_timestamp(self):
        old_password = 'password1'
        new_password = 'eaWrivtig5'
        user = self.create_test_user(password=old_password)
        signer = ResetPasswordSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        data['timestamp'] += 1
        data['password'] = new_password
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_invalid_response(response, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertTrue(user.check_password(old_password))

    def test_reset_expired(self):
        timestamp = int(time.time())
        old_password = 'password1'
        new_password = 'eaWrivtig5'
        user = self.create_test_user(password=old_password)
        with patch('time.time',
                   side_effect=lambda: timestamp):
            signer = ResetPasswordSigner({'user_id': user.pk})
            data = signer.get_signed_data()
        data['password'] = new_password
        request = self.create_post_request(data)
        with patch('time.time',
                   side_effect=lambda: timestamp + 3600 * 24 * 8):
            response = self.view_func(request)
        self.assert_invalid_response(response, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertTrue(user.check_password(old_password))


@pytest.fixture()
def api_view_provider():
    return ViewProvider('reset-password')


@pytest.fixture()
def user_signed_data(user):
    user_reset_password_signer = ResetPasswordSigner({'user_id': user.pk})
    return user_reset_password_signer.get_signed_data()


@pytest.fixture()
def old_password(password_change):
    return password_change.old_value


@pytest.fixture()
def new_password(password_change):
    return password_change.new_value


@override_rest_registration_settings({
    'RESET_PASSWORD_SERIALIZER_PASSWORD_CONFIRM': True,
})
def test_when_confirm_enabled_and_password_confirm_field_then_success(
        settings_with_reset_password_verification,
        user, user_signed_data, new_password,
        api_view_provider, api_factory):
    user_signed_data['password'] = new_password
    user_signed_data['password_confirm'] = new_password
    request = api_factory.create_post_request(user_signed_data)
    response = api_view_provider.view_func(request)

    assert_response_is_ok(response)
    user.refresh_from_db()
    assert user.check_password(new_password)


@override_rest_registration_settings({
    'RESET_PASSWORD_SERIALIZER_PASSWORD_CONFIRM': True,
})
def test_when_confirm_enabled_and_no_password_confirm_field_then_failure(
        settings_with_reset_password_verification,
        user, user_signed_data, old_password, new_password,
        api_view_provider, api_factory):
    user_signed_data['password'] = new_password
    request = api_factory.create_post_request(user_signed_data)
    response = api_view_provider.view_func(request)

    assert_response_is_bad_request(response)
    user.refresh_from_db()
    assert user.check_password(old_password)


@override_rest_registration_settings({
    'RESET_PASSWORD_SERIALIZER_PASSWORD_CONFIRM': True,
})
def test_when_confirm_enabled_and_invalid_password_confirm_field_then_failure(
        settings_with_reset_password_verification,
        user, user_signed_data, old_password, new_password,
        api_view_provider, api_factory):
    user_signed_data['password'] = new_password
    user_signed_data['password_confirm'] = new_password + 'x'
    request = api_factory.create_post_request(user_signed_data)
    response = api_view_provider.view_func(request)

    assert_response_is_bad_request(response)
    user.refresh_from_db()
    assert user.check_password(old_password)


@pytest.mark.parametrize("new_weak_password,expected_error_message", [
    (
        'ftayx',
        'This password is too short. It must contain at least 8 characters.'
    ),
    (
        '563495763456',
        'This password is entirely numeric.'
    ),
    (
        'creative',
        'This password is too common.'
    ),
])
def test_when_weak_password_then_failure(
        settings_with_reset_password_verification,
        user, user_signed_data, old_password, new_weak_password,
        expected_error_message,
        api_view_provider, api_factory):
    user_signed_data['password'] = new_weak_password
    request = api_factory.create_post_request(user_signed_data)
    response = api_view_provider.view_func(request)

    _assert_response_is_bad_password(response, expected_error_message)
    user.refresh_from_db()
    assert user.check_password(old_password)


def test_when_password_same_as_username_then_failure(
        settings_with_reset_password_verification,
        user, user_signed_data, old_password,
        api_view_provider, api_factory):
    user_signed_data['password'] = user.username
    request = api_factory.create_post_request(user_signed_data)
    response = api_view_provider.view_func(request)

    assert_response_is_bad_request(response)
    user.refresh_from_db()
    assert user.check_password(old_password)


def _assert_response_is_bad_password(request, expected_error_message):
    assert_response_is_bad_request(request)
    assert isinstance(request.data, dict)
    assert 'password' in request.data
    password_errors = request.data['password']
    assert len(password_errors) == 1
    error_message = password_errors[0]
    assert error_message == expected_error_message

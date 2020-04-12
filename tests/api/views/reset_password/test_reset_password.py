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

    def test_reset_short_password(self):
        old_password = 'password1'
        new_password = 'c'
        user = self.create_test_user(password=old_password)
        signer = ResetPasswordSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        data['password'] = new_password
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_response_is_bad_request(response)
        user.refresh_from_db()
        self.assertTrue(user.check_password(old_password))

    def test_reset_numeric_password(self):
        old_password = 'password1'
        new_password = '563495763456'
        user = self.create_test_user(password=old_password)
        signer = ResetPasswordSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        data['password'] = new_password
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_response_is_bad_request(response)
        user.refresh_from_db()
        self.assertTrue(user.check_password(old_password))

    def test_reset_password_same_as_username(self):
        username = 'albert.einstein'
        old_password = 'password1'
        new_password = username
        user = self.create_test_user(username=username, password=old_password)
        signer = ResetPasswordSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        data['password'] = new_password
        request = self.create_post_request(data)
        response = self.view_func(request)
        self.assert_response_is_bad_request(response)
        user.refresh_from_db()
        self.assertTrue(user.check_password(old_password))

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


@override_rest_registration_settings({
    'RESET_PASSWORD_SERIALIZER_PASSWORD_CONFIRM': True
})
def test_when_confirm_enabled_and_password_confirm_field_then_reset_password_succeeds(  # noqa: E501
        settings_with_reset_password_verification,
        user, password_change,
        api_view_provider, api_factory):
    new_password = password_change.new_value
    signer = ResetPasswordSigner({'user_id': user.pk})
    data = signer.get_signed_data()
    data['password'] = new_password
    data['password_confirm'] = new_password
    request = api_factory.create_post_request(data)
    response = api_view_provider.view_func(request)

    assert_response_is_ok(response)
    user.refresh_from_db()
    assert user.check_password(new_password)


@override_rest_registration_settings({
    'RESET_PASSWORD_SERIALIZER_PASSWORD_CONFIRM': True
})
def test_when_confirm_enabled_and_no_password_confirm_field_then_reset_password_fails(  # noqa: E501
        settings_with_reset_password_verification,
        user, password_change,
        api_view_provider, api_factory):
    old_password = password_change.old_value
    new_password = password_change.new_value
    signer = ResetPasswordSigner({'user_id': user.pk})
    data = signer.get_signed_data()
    data['password'] = new_password
    request = api_factory.create_post_request(data)
    response = api_view_provider.view_func(request)

    assert_response_is_bad_request(response)
    user.refresh_from_db()
    assert user.check_password(old_password)


@override_rest_registration_settings({
    'RESET_PASSWORD_SERIALIZER_PASSWORD_CONFIRM': True
})
def test_when_confirm_enabled_and_invalid_password_confirm_field_then_reset_password_fails(  # noqa: E501
        settings_with_reset_password_verification,
        user, password_change,
        api_view_provider, api_factory):
    old_password = password_change.old_value
    new_password = password_change.new_value
    signer = ResetPasswordSigner({'user_id': user.pk})
    data = signer.get_signed_data()
    data['password'] = new_password
    data['password_confirm'] = new_password + 'x'
    request = api_factory.create_post_request(data)
    response = api_view_provider.view_func(request)

    assert_response_is_bad_request(response)
    user.refresh_from_db()
    assert user.check_password(old_password)

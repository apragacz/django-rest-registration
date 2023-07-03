import time
from unittest import mock
from unittest.mock import patch

import pytest

from rest_registration.api.views.register import RegisterSigner
from tests.helpers.api_views import (
    assert_response_status_is_bad_request,
    assert_response_status_is_not_found,
    assert_response_status_is_ok
)
from tests.helpers.constants import REGISTER_VERIFICATION_URL
from tests.helpers.settings import override_rest_registration_settings
from tests.helpers.views import ViewProvider


def test_ok(
    settings_with_register_verification,
    api_view_provider, api_factory, inactive_user,
):
    user = inactive_user
    assert not user.is_active
    request = prepare_request(api_factory, user)
    response = api_view_provider.view_func(request)
    assert_response_status_is_ok(response)
    user.refresh_from_db()
    assert user.is_active


@override_rest_registration_settings({
    'USER_VERIFICATION_ID_FIELD': 'username',
})
def test_ok_with_username_as_verification_id(
    settings_with_register_verification,
    api_view_provider, api_factory, inactive_user,
):
    user = inactive_user
    request = prepare_request(
        api_factory,
        user,
        data_to_sign={'user_id': user.username},
    )
    response = api_view_provider.view_func(request)
    assert_response_status_is_ok(response)
    user.refresh_from_db()
    assert user.is_active


def test_ok_idempotent(
    settings_with_register_verification,
    api_view_provider, api_factory, inactive_user,
):
    user = inactive_user
    request1 = prepare_request(api_factory, user)
    request2 = prepare_request(api_factory, user)

    api_view_provider.view_func(request1)

    response = api_view_provider.view_func(request2)
    assert_response_status_is_ok(response)
    user.refresh_from_db()
    assert user.is_active


@override_rest_registration_settings({
    'REGISTER_VERIFICATION_ONE_TIME_USE': True,
})
def test_ok_then_fail_with_one_time_use(
    settings_with_register_verification,
    api_view_provider, api_factory, inactive_user,
):
    user = inactive_user
    request1 = prepare_request(api_factory, user)
    request2 = prepare_request(api_factory, user)

    response1 = api_view_provider.view_func(request1)
    assert_response_status_is_ok(response1)
    user.refresh_from_db()
    assert user.is_active

    response2 = api_view_provider.view_func(request2)
    assert_response_status_is_bad_request(response2)
    user.refresh_from_db()
    assert user.is_active


@override_rest_registration_settings({
    'REGISTER_VERIFICATION_AUTO_LOGIN': True,
})
def test_ok_login(
    settings_with_register_verification,
    api_view_provider, api_factory, inactive_user,
):
    user = inactive_user
    with patch('django.contrib.auth.login') as login_mock:
        request = prepare_request(api_factory, user)
        response = api_view_provider.view_func(request)
        login_mock.assert_called_once_with(
            mock.ANY,
            user,
            backend='django.contrib.auth.backends.ModelBackend')
    assert_response_status_is_ok(response)
    user.refresh_from_db()
    assert user.is_active


def test_fail_when_tampered_timestamp(
    settings_with_register_verification,
    api_view_provider, api_factory, inactive_user,
):
    user = inactive_user
    assert not user.is_active
    signer = RegisterSigner({'user_id': user.pk})
    data = signer.get_signed_data()
    data['timestamp'] += 1
    request = api_factory.create_post_request(data)
    response = api_view_provider.view_func(request)
    assert_response_status_is_bad_request(response)
    user.refresh_from_db()
    assert not user.is_active


def test_fail_when_expired(
    settings_with_register_verification,
    api_view_provider, api_factory, inactive_user,
):
    user = inactive_user
    assert not user.is_active
    timestamp = int(time.time())
    with patch(
        'time.time',
        side_effect=lambda: timestamp,
    ):
        signer = RegisterSigner({'user_id': user.pk})
        data = signer.get_signed_data()
        request = api_factory.create_post_request(data)

    with patch(
        'time.time',
        side_effect=lambda: timestamp + 3600 * 24 * 8,
    ):
        response = api_view_provider.view_func(request)
    assert_response_status_is_bad_request(response)
    user.refresh_from_db()
    assert not user.is_active


@override_rest_registration_settings({
    'REGISTER_VERIFICATION_ENABLED': False,
    'REGISTER_VERIFICATION_URL': REGISTER_VERIFICATION_URL,
})
def test_fail_when_disabled(
    settings_with_register_verification,
    api_view_provider, api_factory, inactive_user,
):
    user = inactive_user
    request = prepare_request(api_factory, user)

    response = api_view_provider.view_func(request)

    assert_response_status_is_not_found(response)
    user.refresh_from_db()
    assert not user.is_active


@pytest.fixture()
def api_view_provider():
    return ViewProvider('verify-registration')


def prepare_request(api_factory, user, session=False, data_to_sign=None):
    if data_to_sign is None:
        data_to_sign = {'user_id': user.pk}
    signer = RegisterSigner(data_to_sign)
    data = signer.get_signed_data()
    request = api_factory.create_post_request(data)
    if session:
        api_factory.add_session_to_request(request)
    return request

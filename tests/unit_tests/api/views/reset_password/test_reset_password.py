import time
from unittest.mock import patch

import pytest
from rest_framework.exceptions import ErrorDetail

from rest_registration.api.views.reset_password import ResetPasswordSigner
from tests.helpers.api_views import (
    assert_response_is_bad_request,
    assert_response_is_not_found,
    assert_response_is_ok,
)
from tests.helpers.settings import override_rest_registration_settings
from tests.helpers.views import ViewProvider


def test_reset_ok(
    settings_with_reset_password_verification,
    api_view_provider,
    api_factory,
    user,
    user_signed_data,
    new_password,
):
    user_signed_data["password"] = new_password
    request = api_factory.create_post_request(user_signed_data)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    user.refresh_from_db()
    assert user.check_password(new_password)


@override_rest_registration_settings(
    {
        "USER_VERIFICATION_ID_FIELD": "username",
    }
)
def test_reset_with_username_as_verification_id_ok(
    settings_with_reset_password_verification,
    api_view_provider,
    api_factory,
    user,
    new_password,
):
    signer = ResetPasswordSigner({"user_id": user.username})
    data = signer.get_signed_data()
    data["password"] = new_password
    request = api_factory.create_post_request(data)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    user.refresh_from_db()
    assert user.check_password(new_password)


def test_reset_twice_ok(
    settings_with_reset_password_verification,
    api_view_provider,
    api_factory,
    user,
    user_signed_data,
):
    new_first_password = "eaWrivtig5"
    new_second_password = "eaWrivtig6"
    user_signed_data["password"] = new_first_password
    request = api_factory.create_post_request(user_signed_data)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    user.refresh_from_db()
    assert user.check_password(new_first_password)
    user_signed_data["password"] = new_second_password
    request = api_factory.create_post_request(user_signed_data)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    user.refresh_from_db()
    assert user.check_password(new_second_password)


@override_rest_registration_settings(
    {
        "RESET_PASSWORD_VERIFICATION_ONE_TIME_USE": True,
    }
)
def test_one_time_reset_twice_fail(
    settings_with_reset_password_verification,
    api_view_provider,
    api_factory,
    user,
):
    new_first_password = "eaWrivtig5"
    new_second_password = "eaWrivtig6"
    signer = ResetPasswordSigner({"user_id": user.pk})
    user_signed_data = signer.get_signed_data()
    user_signed_data["password"] = new_first_password
    request = api_factory.create_post_request(user_signed_data)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    user.refresh_from_db()
    assert user.check_password(new_first_password)
    user_signed_data["password"] = new_second_password
    request = api_factory.create_post_request(user_signed_data)
    response = api_view_provider.view_func(request)
    assert_response_is_bad_request(response)
    user.refresh_from_db()
    assert user.check_password(new_first_password)


def test_reset_password_disabled(
    settings_minimal,
    api_view_provider,
    api_factory,
    user,
    old_password,
    new_password,
):
    signer = ResetPasswordSigner({"user_id": user.pk}, strict=False)
    user_signed_data = signer.get_signed_data()
    user_signed_data["password"] = new_password
    request = api_factory.create_post_request(user_signed_data)
    response = api_view_provider.view_func(request)
    assert_response_is_not_found(response)
    user.refresh_from_db()
    assert user.check_password(old_password)


def test_reset_unverified_user(
    settings_with_reset_password_verification,
    api_view_provider,
    api_factory,
    user,
    user_signed_data,
    new_password,
):
    user.is_active = False
    user.save()
    user_signed_data["password"] = new_password
    request = api_factory.create_post_request(user_signed_data)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    user.refresh_from_db()
    assert user.check_password(new_password)


def test_reset_tampered_timestamp(
    settings_with_reset_password_verification,
    api_view_provider,
    api_factory,
    user,
    user_signed_data,
    old_password,
    new_password,
):
    user_signed_data["timestamp"] += 1
    user_signed_data["password"] = new_password
    request = api_factory.create_post_request(user_signed_data)
    response = api_view_provider.view_func(request)
    assert_response_is_bad_request(response)
    user.refresh_from_db()
    assert user.check_password(old_password)


def test_reset_expired(
    settings_with_reset_password_verification,
    api_view_provider,
    api_factory,
    user,
    old_password,
    new_password,
):
    timestamp = int(time.time())
    with patch("time.time", side_effect=lambda: timestamp):
        signer = ResetPasswordSigner({"user_id": user.pk})
        user_signed_data = signer.get_signed_data()

    user_signed_data["password"] = new_password
    request = api_factory.create_post_request(user_signed_data)

    with patch("time.time", side_effect=lambda: timestamp + 3600 * 24 * 8):
        response = api_view_provider.view_func(request)
    assert_response_is_bad_request(response)
    user.refresh_from_db()
    assert user.check_password(old_password)


@pytest.fixture
def api_view_provider():
    return ViewProvider("reset-password")


@pytest.fixture
def user_signed_data(user):
    user_reset_password_signer = ResetPasswordSigner({"user_id": user.pk})
    return user_reset_password_signer.get_signed_data()


@pytest.fixture
def old_password(password_change):
    return password_change.old_value


@pytest.fixture
def new_password(password_change):
    return password_change.new_value


@override_rest_registration_settings(
    {
        "RESET_PASSWORD_SERIALIZER_PASSWORD_CONFIRM": True,
    }
)
def test_when_confirm_enabled_and_password_confirm_field_then_success(
    settings_with_reset_password_verification,
    user,
    user_signed_data,
    new_password,
    api_view_provider,
    api_factory,
):
    user_signed_data["password"] = new_password
    user_signed_data["password_confirm"] = new_password
    request = api_factory.create_post_request(user_signed_data)
    response = api_view_provider.view_func(request)

    assert_response_is_ok(response)
    user.refresh_from_db()
    assert user.check_password(new_password)


@override_rest_registration_settings(
    {
        "RESET_PASSWORD_SERIALIZER_PASSWORD_CONFIRM": True,
    }
)
def test_when_confirm_enabled_and_no_password_confirm_field_then_failure(
    settings_with_reset_password_verification,
    user,
    user_signed_data,
    old_password,
    new_password,
    api_view_provider,
    api_factory,
):
    user_signed_data["password"] = new_password
    request = api_factory.create_post_request(user_signed_data)
    response = api_view_provider.view_func(request)

    assert_response_is_bad_request(response)
    user.refresh_from_db()
    assert user.check_password(old_password)


@override_rest_registration_settings(
    {
        "RESET_PASSWORD_SERIALIZER_PASSWORD_CONFIRM": True,
    }
)
def test_when_confirm_enabled_and_invalid_password_confirm_field_then_failure(
    settings_with_reset_password_verification,
    user,
    user_signed_data,
    old_password,
    new_password,
    api_view_provider,
    api_factory,
):
    user_signed_data["password"] = new_password
    user_signed_data["password_confirm"] = new_password + "x"
    request = api_factory.create_post_request(user_signed_data)
    response = api_view_provider.view_func(request)

    assert_response_is_bad_request(response)
    user.refresh_from_db()
    assert user.check_password(old_password)


@pytest.mark.parametrize(
    ("new_weak_password", "expected_error_message", "expected_error_code"),
    [
        pytest.param(
            "ftayx",
            "This password is too short. It must contain at least 8 characters.",
            "password_too_short",
            id="too short",
        ),
        pytest.param(
            "563495763456",
            "This password is entirely numeric.",
            "password_entirely_numeric",
            id="entirely numeric",
        ),
        pytest.param(
            "creative",
            "This password is too common.",
            "password_too_common",
            id="too common",
        ),
    ],
)
def test_when_weak_password_then_failure(
    settings_with_reset_password_verification,
    user,
    user_signed_data,
    old_password,
    api_view_provider,
    api_factory,
    new_weak_password,
    expected_error_message,
    expected_error_code,
):
    user_signed_data["password"] = new_weak_password
    request = api_factory.create_post_request(user_signed_data)
    response = api_view_provider.view_func(request)

    _assert_response_is_bad_password(
        response, expected_error_message, expected_error_code
    )
    user.refresh_from_db()
    assert user.check_password(old_password)


def test_when_password_same_as_username_then_failure(
    settings_with_reset_password_verification,
    user,
    user_signed_data,
    old_password,
    api_view_provider,
    api_factory,
):
    user_signed_data["password"] = user.username
    request = api_factory.create_post_request(user_signed_data)
    response = api_view_provider.view_func(request)

    assert_response_is_bad_request(response)
    user.refresh_from_db()
    assert user.check_password(old_password)


def _assert_response_is_bad_password(
    request,
    expected_error_message,
    expected_error_code,
):
    assert_response_is_bad_request(request)
    assert isinstance(request.data, dict)
    assert "password" in request.data
    password_errors = request.data["password"]
    assert len(password_errors) == 1
    err = password_errors[0]
    assert isinstance(err, ErrorDetail)
    assert err == expected_error_message
    assert err.code == expected_error_code

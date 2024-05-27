import time
from unittest.mock import patch

import pytest
from django.test.utils import override_settings

from rest_registration.api.views.register_email import RegisterEmailSigner
from tests.helpers.api_views import (
    assert_response_is_bad_request,
    assert_response_is_not_found,
    assert_response_is_ok,
)
from tests.helpers.constants import REGISTER_EMAIL_VERIFICATION_URL
from tests.helpers.settings import override_rest_registration_settings
from tests.helpers.views import ViewProvider


def test_ok(
    settings_with_register_email_verification,
    user,
    email_change,
    signer,
    api_view_provider,
    api_factory,
    assert_email_changed,
):
    data = signer.get_signed_data()
    request = api_factory.create_post_request(data)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_email_changed()


def test_new_email_already_in_use_ok(
    settings_with_register_email_verification,
    user,
    user2_with_user_new_email,
    signer,
    api_view_provider,
    api_factory,
    assert_email_changed,
):
    data = signer.get_signed_data()
    request = api_factory.create_post_request(data)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_email_changed()


@override_rest_registration_settings(
    {
        "USER_VERIFICATION_ID_FIELD": "username",
    }
)
def test_with_username_as_verification_id_ok(
    settings_with_register_email_verification,
    user,
    email_change,
    api_view_provider,
    api_factory,
    assert_email_changed,
):
    signer = RegisterEmailSigner(
        {
            "user_id": user.username,
            "email": email_change.new_value,
        }
    )
    data = signer.get_signed_data()
    request = api_factory.create_post_request(data)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_email_changed()


@override_settings(
    REST_REGISTRATION={
        "REGISTER_EMAIL_VERIFICATION_URL": REGISTER_EMAIL_VERIFICATION_URL,
    }
)
def test_inactive_user(
    settings_with_register_email_verification,
    user,
    signer,
    api_view_provider,
    api_factory,
    assert_email_not_changed,
):
    user.is_active = False
    user.save()
    data = signer.get_signed_data()
    request = api_factory.create_post_request(data)
    response = api_view_provider.view_func(request)
    assert_response_is_bad_request(response)
    assert_email_not_changed()


def test_noverify_not_found(
    user,
    email_change,
    api_view_provider,
    api_factory,
    assert_email_not_changed,
):
    signer = RegisterEmailSigner(
        {
            "user_id": user.pk,
            "email": email_change.new_value,
        },
        strict=False,
    )
    data = signer.get_signed_data()
    request = api_factory.create_post_request(data)
    response = api_view_provider.view_func(request)
    assert_response_is_not_found(response)
    assert_email_not_changed()


def test_tampered_timestamp(
    settings_with_register_email_verification,
    user,
    signer,
    api_view_provider,
    api_factory,
    assert_email_not_changed,
):
    data = signer.get_signed_data()
    data["timestamp"] += 1
    request = api_factory.create_post_request(data)
    response = api_view_provider.view_func(request)
    assert_response_is_bad_request(response)
    assert_email_not_changed()


def test_tampered_email(
    settings_with_register_email_verification,
    user,
    signer,
    api_view_provider,
    api_factory,
    assert_email_not_changed,
):
    data = signer.get_signed_data()
    data["email"] = "p" + data["email"]
    request = api_factory.create_post_request(data)
    response = api_view_provider.view_func(request)
    assert_response_is_bad_request(response)
    assert_email_not_changed()


def test_expired(
    settings_with_register_email_verification,
    user,
    email_change,
    api_view_provider,
    api_factory,
    assert_email_not_changed,
):
    timestamp = time.time()
    with patch("time.time", side_effect=lambda: timestamp):
        signer = RegisterEmailSigner(
            {
                "user_id": user.pk,
                "email": email_change.new_value,
            }
        )
        data = signer.get_signed_data()
    request = api_factory.create_post_request(data)
    with patch("time.time", side_effect=lambda: timestamp + 3600 * 24 * 8):
        response = api_view_provider.view_func(request)
    assert_response_is_bad_request(response)
    assert_email_not_changed()


def test_user_with_unique_email_user_email_already_exists(
    settings_with_register_email_verification,
    settings_with_user_with_unique_email,
    user,
    user2_with_user_new_email,
    signer,
    api_view_provider,
    api_factory,
    assert_email_not_changed,
):
    data = signer.get_signed_data()
    request = api_factory.create_post_request(data)
    response = api_view_provider.view_func(request)
    assert_response_is_bad_request(response)
    assert_email_not_changed()


@override_rest_registration_settings(
    {"USE_NON_FIELD_ERRORS_KEY_FROM_DRF_SETTINGS": True}
)
def test_user_with_unique_email_user_email_already_exists_non_field_errors(
    settings_with_register_email_verification,
    settings_with_user_with_unique_email,
    user,
    user2_with_user_new_email,
    signer,
    api_view_provider,
    api_factory,
    assert_email_not_changed,
):
    data = signer.get_signed_data()
    request = api_factory.create_post_request(data)
    response = api_view_provider.view_func(request)
    assert_response_is_bad_request(response)
    assert "non_field_errors" in response.data
    assert_email_not_changed()


@pytest.fixture
def signer(user, email_change):
    return RegisterEmailSigner(
        {
            "user_id": user.pk,
            "email": email_change.new_value,
        }
    )


@pytest.fixture
def assert_email_changed(user, email_change):
    def assertion():
        user.refresh_from_db()
        assert user.email == email_change.new_value

    return assertion


@pytest.fixture
def assert_email_not_changed(user, email_change):
    def assertion():
        user.refresh_from_db()
        assert user.email == email_change.old_value

    return assertion


@pytest.fixture
def api_view_provider():
    return ViewProvider("verify-email")

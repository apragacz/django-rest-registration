from unittest import mock

import pytest
from django.core import signing
from rest_framework.test import force_authenticate

from rest_registration.api.views.register_email import RegisterEmailSigner
from rest_registration.exceptions import SignatureExpired, SignatureInvalid
from rest_registration.utils.verification import verify_signer_or_bad_request
from tests.helpers.api_views import (
    assert_response_is_bad_request,
    assert_response_is_ok,
)
from tests.helpers.constants import (
    REGISTER_EMAIL_VERIFICATION_URL,
    VERIFICATION_FROM_EMAIL,
)
from tests.helpers.email import (
    assert_no_email_sent,
    assert_one_email_sent,
    capture_sent_emails,
)
from tests.helpers.settings import override_rest_registration_settings
from tests.helpers.text import assert_no_url_in_text, assert_one_url_line_in_text
from tests.helpers.timer import capture_time
from tests.helpers.verification import assert_valid_verification_url
from tests.helpers.views import ViewProvider


def test_ok(
    settings_with_register_email_verification,
    user,
    email_change,
    api_view_provider,
    api_factory,
):
    new_email = email_change.new_value
    request = api_factory.create_post_request(
        {
            "email": new_email,
        }
    )
    force_authenticate(request, user=user)
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_one_email_sent(sent_emails)
    sent_email = sent_emails[0]
    assert_valid_register_email_verification_email(sent_email, user, new_email, timer)
    user.refresh_from_db()
    assert user.email == email_change.old_value


def test_email_already_in_use_ok(
    settings_with_register_email_verification,
    user,
    user2_with_user_new_email,
    email_change,
    api_view_provider,
    api_factory,
):
    new_email = email_change.new_value
    request = api_factory.create_post_request(
        {
            "email": new_email,
        }
    )
    force_authenticate(request, user=user)
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    user.refresh_from_db()
    assert user.email == email_change.old_value
    assert_one_email_sent(sent_emails)
    sent_email = sent_emails[0]
    assert_valid_register_email_verification_email(sent_email, user, new_email, timer)


def test_user_with_unique_email_ok_but_notification_already_exists(
    settings_with_user_with_unique_email,
    settings_with_register_email_verification,
    user,
    user2_with_user_new_email,
    email_change,
    api_view_provider,
    api_factory,
):
    new_email = email_change.new_value
    request = api_factory.create_post_request(
        {
            "email": new_email,
        }
    )
    force_authenticate(request, user=user)
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)

    assert_response_is_ok(response)
    user.refresh_from_db()
    assert user.email == email_change.old_value
    assert_one_email_sent(sent_emails)
    sent_email = sent_emails[0]
    assert_already_exists_email(sent_email, new_email)


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
):
    new_email = email_change.new_value
    request = api_factory.create_post_request(
        {
            "email": new_email,
        }
    )
    force_authenticate(request, user=user)
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    user.refresh_from_db()
    assert user.email == email_change.old_value
    assert_one_email_sent(sent_emails)
    sent_email = sent_emails[0]
    assert_valid_register_email_verification_email(
        sent_email,
        user,
        new_email,
        timer,
        user_id_attr="username",
        user_id_type=str,
    )


@override_rest_registration_settings(
    {
        "REGISTER_EMAIL_VERIFICATION_ENABLED": False,
    }
)
def test_noverify_ok(
    user,
    email_change,
    api_view_provider,
    api_factory,
):
    new_email = email_change.new_value
    request = api_factory.create_post_request(
        {
            "email": new_email,
        }
    )
    force_authenticate(request, user=user)
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    user.refresh_from_db()
    assert user.email == new_email
    assert_no_email_sent(sent_emails)


@override_rest_registration_settings(
    {"USE_NON_FIELD_ERRORS_KEY_FROM_DRF_SETTINGS": True}
)
@pytest.mark.parametrize(
    ("exception", "expected"),
    [
        (signing.SignatureExpired, SignatureExpired),
        (signing.BadSignature, SignatureInvalid),
    ],
)
def test_verify_signer_or_bad_request_non_field_errors(exception, expected):
    # arrange
    mock_signer = mock.MagicMock()
    mock_verify = mock.Mock(side_effect=exception())
    mock_signer.verify = mock_verify

    # act, assert
    with pytest.raises(expected) as context:
        verify_signer_or_bad_request(mock_signer)

    assert "non_field_errors" in context.value.get_full_details()


@override_rest_registration_settings(
    {
        "REGISTER_EMAIL_VERIFICATION_ENABLED": False,
        "USE_NON_FIELD_ERRORS_KEY_FROM_DRF_SETTINGS": True,
    }
)
def test_register_email_fail_with_non_field_errors(
    settings_with_simple_email_based_user, user, api_view_provider, api_factory
):
    request = api_factory.create_post_request(
        {
            "email": user.email,
        }
    )
    force_authenticate(request, user=user)
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_no_email_sent(sent_emails)
    assert_response_is_bad_request(response)
    assert "non_field_errors" in response.data


@override_rest_registration_settings({"REGISTER_EMAIL_VERIFICATION_ENABLED": False})
def test_register_email_fail_email_already_used(
    settings_with_simple_email_based_user, user, api_view_provider, api_factory
):
    request = api_factory.create_post_request(
        {
            "email": user.email,
        }
    )
    force_authenticate(request, user=user)
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_no_email_sent(sent_emails)
    assert_response_is_bad_request(response)
    assert "detail" in response.data


@override_rest_registration_settings(
    {
        "VERIFICATION_TEMPLATES_SELECTOR": "tests.testapps.custom_templates.utils.select_verification_templates",  # noqa E501
    }
)
def test_ok_when_custom_verification_templates_selector(
    settings_with_register_email_verification,
    user,
    email_change,
    api_view_provider,
    api_factory,
):
    new_email = email_change.new_value
    request = api_factory.create_post_request(
        {
            "email": new_email,
        }
    )
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


@pytest.fixture
def api_view_provider():
    return ViewProvider("register-email")


def assert_valid_register_email_verification_email(
    sent_email,
    user,
    new_email,
    timer,
    user_id_attr="pk",
    user_id_type=int,
):
    assert sent_email.from_email == VERIFICATION_FROM_EMAIL
    assert sent_email.to == [new_email]
    url = assert_one_url_line_in_text(sent_email.body)

    verification_data = assert_valid_verification_url(
        url,
        expected_path=REGISTER_EMAIL_VERIFICATION_URL,
        expected_fields={"signature", "user_id", "timestamp", "email"},
        timer=timer,
        signer_cls=RegisterEmailSigner,
    )
    url_user_id = user_id_type(verification_data["user_id"])
    assert url_user_id == getattr(user, user_id_attr)


def assert_already_exists_email(sent_email, new_email):
    assert sent_email.from_email == VERIFICATION_FROM_EMAIL
    assert sent_email.to == [new_email]

    assert "already in use" in sent_email.subject
    assert "this e-mail for which there is an existing account" in sent_email.body
    assert_no_url_in_text(sent_email.body)

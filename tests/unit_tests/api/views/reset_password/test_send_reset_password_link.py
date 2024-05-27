import pytest
from django.test.utils import override_settings

from rest_registration.api.views.reset_password import ResetPasswordSigner
from tests.helpers.api_views import (
    assert_response_is_bad_request,
    assert_response_is_not_found,
    assert_response_is_ok,
)
from tests.helpers.constants import (
    RESET_PASSWORD_VERIFICATION_URL,
    VERIFICATION_FROM_EMAIL,
)
from tests.helpers.email import (
    assert_no_email_sent,
    assert_one_email_sent,
    capture_sent_emails,
)
from tests.helpers.settings import override_rest_registration_settings
from tests.helpers.text import assert_one_url_line_in_text
from tests.helpers.timer import capture_time
from tests.helpers.verification import assert_valid_verification_url
from tests.helpers.views import ViewProvider


def test_send_link_ok(
    settings_with_reset_password_verification,
    api_view_provider,
    api_factory,
    user,
):
    request = api_factory.create_post_request(
        {
            "login": user.username,
        }
    )
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_one_email_sent(sent_emails)

    sent_email = sent_emails[0]
    assert_valid_send_link_email(sent_email, user, timer)


@override_rest_registration_settings(
    {
        "USER_VERIFICATION_ID_FIELD": "username",
    }
)
def test_send_link_with_username_as_verification_id_ok(
    settings_with_reset_password_verification,
    api_view_provider,
    api_factory,
    user,
):
    request = api_factory.create_post_request(
        {
            "login": user.username,
        }
    )
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_one_email_sent(sent_emails)

    sent_email = sent_emails[0]
    assert_valid_send_link_email(
        sent_email, user, timer, user_id_attr="username", user_id_type=str
    )


def test_send_link_but_email_not_in_login_fields(
    settings_with_reset_password_verification,
    api_view_provider,
    api_factory,
    user,
):
    request = api_factory.create_post_request(
        {
            "login": user.email,
        }
    )
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_response_is_bad_request(response)
    assert_no_email_sent(sent_emails)


@override_rest_registration_settings(
    {
        "USER_LOGIN_FIELDS": ["username", "email"],
    }
)
def test_send_link_via_login_username_ok(
    settings_with_reset_password_verification,
    api_view_provider,
    api_factory,
    user,
):
    request = api_factory.create_post_request(
        {
            "login": user.username,
        }
    )
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_one_email_sent(sent_emails)

    sent_email = sent_emails[0]
    assert_valid_send_link_email(sent_email, user, timer)


@override_rest_registration_settings(
    {
        "USER_LOGIN_FIELDS": ["username", "email"],
    }
)
def test_send_link_via_login_email_ok(
    settings_with_reset_password_verification,
    api_view_provider,
    api_factory,
    user,
):
    request = api_factory.create_post_request(
        {
            "login": user.email,
        }
    )
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_one_email_sent(sent_emails)

    sent_email = sent_emails[0]
    assert_valid_send_link_email(sent_email, user, timer)


@override_rest_registration_settings(
    {
        "USER_LOGIN_FIELDS": ["username", "email"],
        "SEND_RESET_PASSWORD_LINK_SERIALIZER_USE_EMAIL": True,
    }
)
def test_send_link_via_email_ok(
    settings_with_reset_password_verification,
    api_view_provider,
    api_factory,
    user,
):
    request = api_factory.create_post_request(
        {
            "email": user.email,
        }
    )
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_one_email_sent(sent_emails)

    sent_email = sent_emails[0]
    assert_valid_send_link_email(sent_email, user, timer)


def test_send_link_unverified_user(
    settings_with_reset_password_verification,
    api_view_provider,
    api_factory,
    user,
):
    user.is_active = False
    user.save()
    request = api_factory.create_post_request(
        {
            "login": user.username,
        }
    )
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_one_email_sent(sent_emails)

    sent_email = sent_emails[0]
    assert_valid_send_link_email(sent_email, user, timer)


@override_rest_registration_settings(
    {
        "RESET_PASSWORD_VERIFICATION_ONE_TIME_USE": True,
    }
)
def test_send_link_unverified_user_one_time_use(
    settings_with_reset_password_verification,
    api_view_provider,
    api_factory,
    user,
):
    user.is_active = False
    user.save()
    request = api_factory.create_post_request(
        {
            "login": user.username,
        }
    )
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_one_email_sent(sent_emails)

    sent_email = sent_emails[0]
    assert_valid_send_link_email(sent_email, user, timer)


def test_reset_password_disabled(
    settings_minimal,
    api_view_provider,
    api_factory,
    user,
):
    request = api_factory.create_post_request(
        {
            "login": user.username,
        }
    )
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_no_email_sent(sent_emails)
    assert_response_is_not_found(response)


@override_settings(
    TEMPLATES=(),
)
def test_no_templates_reset_password_disabled(
    settings_minimal,
    api_view_provider,
    api_factory,
    user,
):
    request = api_factory.create_post_request(
        {
            "login": user.username,
        }
    )
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_no_email_sent(sent_emails)
    assert_response_is_not_found(response)


def test_send_link_invalid_login(
    settings_with_reset_password_verification,
    api_view_provider,
    api_factory,
    user,
):
    request = api_factory.create_post_request(
        {
            "login": user.username + "b",
        }
    )

    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_no_email_sent(sent_emails)
    assert_response_is_bad_request(response)


@pytest.fixture
def api_view_provider():
    return ViewProvider("send-reset-password-link")


def test_when_duplicated_email_then_send_link_via_login_successful(
    settings_with_reset_password_verification,
    api_view_provider,
    api_factory,
    user,
    user2_with_user_email,
):
    request = api_factory.create_post_request(
        {
            "login": user.username,
        }
    )
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_one_email_sent(sent_emails)

    sent_email = sent_emails[0]
    assert_valid_send_link_email(sent_email, user, timer)


def test_when_no_user_reveal_then_send_link_successful(
    settings_with_reset_password_verification,
    settings_with_reset_password_fail_when_user_not_found_disabled,
    api_view_provider,
    api_factory,
    user,
):
    request = api_factory.create_post_request(
        {
            "login": user.username,
        }
    )
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
    api_view_provider,
    api_factory,
):
    request = api_factory.create_post_request(
        {
            "login": "ninja",
        }
    )
    with capture_sent_emails() as sent_emails:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_no_email_sent(sent_emails)


@override_rest_registration_settings(
    {
        "VERIFICATION_TEMPLATES_SELECTOR": "tests.testapps.custom_templates.utils.select_verification_templates",  # noqa E501
    }
)
def test_ok_when_custom_verification_templates_selector(
    settings_with_reset_password_verification, api_view_provider, api_factory, user
):
    request = api_factory.create_post_request(
        {
            "login": user.username,
        }
    )
    with capture_sent_emails() as sent_emails, capture_time() as timer:
        response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert_one_email_sent(sent_emails)

    sent_email = sent_emails[0]
    assert sent_email.subject == "Generic verification link was sent"
    assert sent_email.body.startswith("Click URL to verify:")
    assert_valid_send_link_email(sent_email, user, timer)


def assert_valid_send_link_email(
    sent_email,
    user,
    timer,
    user_id_attr="pk",
    user_id_type=int,
):
    assert sent_email.from_email == VERIFICATION_FROM_EMAIL
    assert sent_email.to == [user.email]
    url = assert_one_url_line_in_text(sent_email.body)
    verification_data = assert_valid_verification_url(
        url,
        expected_path=RESET_PASSWORD_VERIFICATION_URL,
        expected_fields={"signature", "user_id", "timestamp"},
        signer_cls=ResetPasswordSigner,
        timer=timer,
    )
    url_user_id = user_id_type(verification_data["user_id"])
    assert url_user_id == getattr(user, user_id_attr)
    return verification_data

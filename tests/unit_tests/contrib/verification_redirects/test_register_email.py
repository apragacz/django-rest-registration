import pytest
from django.conf import settings
from django.test.utils import override_settings

from rest_registration.api.views.register_email import RegisterEmailSigner
from tests.helpers.views import ViewProvider

VERIFICATION_URL = "/accounts/verify-email/"
SUCCESS_URL = "/accounts/verify-email/success/"
FAILURE_URL = "/accounts/verify-email/failure/"


def test_ok(
    settings_with_verification_redirects_urls,
    settings_with_register_email_verification_redirects,
    view_provider,
    http_client,
    user,
    new_email,
    signed_data,
):
    response = http_client.get(view_provider.view_url, data=signed_data)
    assert response.status_code == 302
    assert response.url == SUCCESS_URL
    user.refresh_from_db()
    assert user.email == new_email


def test_tampered_signature(
    settings_with_verification_redirects_urls,
    settings_with_register_email_verification_redirects,
    view_provider,
    http_client,
    user,
    old_email,
    signed_data,
):
    signed_data["signature"] += "ech"
    response = http_client.get(view_provider.view_url, data=signed_data)
    assert response.status_code == 302
    assert response.url == FAILURE_URL
    user.refresh_from_db()
    assert user.email == old_email


@pytest.fixture
def signed_data(user, new_email):
    signer = RegisterEmailSigner(
        {
            "user_id": user.pk,
            "email": new_email,
        }
    )
    data = signer.get_signed_data()
    return data


@pytest.fixture
def new_email(email_change):
    return email_change.new_value


@pytest.fixture
def old_email(email_change):
    return email_change.old_value


@pytest.fixture
def view_provider(app_name):
    return ViewProvider("verify-email", app_name=app_name)


@pytest.fixture
def settings_with_register_email_verification_redirects():
    with override_settings(
        REST_REGISTRATION={
            "REGISTER_EMAIL_VERIFICATION_ENABLED": True,
            "REGISTER_EMAIL_VERIFICATION_URL": VERIFICATION_URL,
        },
        REST_REGISTRATION_VERIFICATION_REDIRECTS={
            "VERIFY_EMAIL_SUCCESS_URL": SUCCESS_URL,
            "VERIFY_EMAIL_FAILURE_URL": FAILURE_URL,
        },
    ):
        yield settings

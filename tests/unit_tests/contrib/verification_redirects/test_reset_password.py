import pytest
from django.conf import settings
from django.test.utils import override_settings

from rest_registration.api.views.reset_password import ResetPasswordSigner
from tests.helpers.views import ViewProvider

VERIFICATION_URL = "/accounts/reset-password/"
SUCCESS_URL = "/accounts/reset-password/success/"
FAILURE_URL = "/accounts/reset-password/failure/"


def test_ok(
    settings_with_verification_redirects_urls,
    settings_with_reset_password_verification_redirects,
    view_provider,
    http_client,
    user,
    new_password,
    signed_data,
):
    signed_data["password"] = new_password
    response = http_client.post(view_provider.view_url, data=signed_data)
    assert response.status_code == 302
    assert response.url == SUCCESS_URL
    user.refresh_from_db()
    assert user.check_password(new_password)


def test_tampered_signature(
    settings_with_verification_redirects_urls,
    settings_with_reset_password_verification_redirects,
    view_provider,
    http_client,
    user,
    old_password,
    new_password,
    signed_data,
):
    signed_data["password"] = new_password
    signed_data["signature"] += "heh"
    response = http_client.post(view_provider.view_url, data=signed_data)
    assert response.status_code == 302
    assert response.url == FAILURE_URL
    user.refresh_from_db()
    assert user.check_password(old_password)


@pytest.fixture
def signed_data(user):
    signer = ResetPasswordSigner(
        {
            "user_id": user.pk,
        }
    )
    data = signer.get_signed_data()
    return data


@pytest.fixture
def new_password(password_change):
    return password_change.new_value


@pytest.fixture
def old_password(password_change):
    return password_change.old_value


@pytest.fixture
def view_provider(app_name):
    return ViewProvider("reset-password", app_name=app_name)


@pytest.fixture
def settings_with_reset_password_verification_redirects():
    with override_settings(
        REST_REGISTRATION={
            "RESET_PASSWORD_VERIFICATION_URL": VERIFICATION_URL,
        },
        REST_REGISTRATION_VERIFICATION_REDIRECTS={
            "RESET_PASSWORD_SUCCESS_URL": SUCCESS_URL,
            "RESET_PASSWORD_FAILURE_URL": FAILURE_URL,
        },
    ):
        yield settings

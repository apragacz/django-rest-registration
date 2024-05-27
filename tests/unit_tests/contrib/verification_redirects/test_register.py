import pytest
from django.conf import settings
from django.test.utils import override_settings

from rest_registration.api.views.register import RegisterSigner
from tests.helpers.views import ViewProvider

VERIFICATION_URL = "/accounts/verify-account/"
SUCCESS_URL = "/accounts/verify-account/success/"
FAILURE_URL = "/accounts/verify-account/failure/"


def test_ok(
    settings_with_verification_redirects_urls,
    settings_with_register_verification_redirects,
    view_provider,
    http_client,
    inactive_user,
    signed_data,
):
    user = inactive_user
    assert not user.is_active
    response = http_client.get(view_provider.view_url, data=signed_data)
    assert response.status_code == 302
    assert response.url == SUCCESS_URL
    user.refresh_from_db()
    assert user.is_active


def test_tampered_signature(
    settings_with_verification_redirects_urls,
    settings_with_register_verification_redirects,
    view_provider,
    http_client,
    inactive_user,
    signed_data,
):
    user = inactive_user
    assert not user.is_active
    signed_data["signature"] += "blah"
    response = http_client.get(view_provider.view_url, data=signed_data)
    assert response.status_code == 302
    assert response.url == FAILURE_URL
    user.refresh_from_db()
    assert not user.is_active


@pytest.fixture
def signed_data(inactive_user):
    signer = RegisterSigner(
        {
            "user_id": inactive_user.pk,
        }
    )
    data = signer.get_signed_data()
    return data


@pytest.fixture
def view_provider(app_name):
    return ViewProvider("verify-registration", app_name=app_name)


@pytest.fixture
def settings_with_register_verification_redirects():
    with override_settings(
        REST_REGISTRATION={
            "REGISTER_VERIFICATION_ENABLED": True,
            "REGISTER_VERIFICATION_URL": VERIFICATION_URL,
        },
        REST_REGISTRATION_VERIFICATION_REDIRECTS={
            "VERIFY_REGISTRATION_SUCCESS_URL": SUCCESS_URL,
            "VERIFY_REGISTRATION_FAILURE_URL": FAILURE_URL,
        },
    ):
        yield settings

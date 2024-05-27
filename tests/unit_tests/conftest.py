from dataclasses import dataclass

import pytest
from django.conf import settings
from django.test import Client
from django.test.utils import override_settings
from rest_framework.authtoken.models import Token

from tests.helpers.api_views import APIViewRequestFactory
from tests.helpers.common import create_test_user
from tests.helpers.constants import (
    REGISTER_EMAIL_VERIFICATION_URL,
    REGISTER_VERIFICATION_URL,
    RESET_PASSWORD_VERIFICATION_URL,
    USER_PASSWORD,
    USERNAME,
    USERNAME2,
    VERIFICATION_FROM_EMAIL,
)
from tests.helpers.settings import (
    override_auth_model_settings,
    override_rest_registration_settings,
)


@dataclass(frozen=True)
class StrValueChange:
    old_value: str
    new_value: str


@pytest.fixture
def settings_minimal():
    return settings


@pytest.fixture
def settings_without_register_verification():
    with override_rest_registration_settings(
        {
            "REGISTER_VERIFICATION_ENABLED": False,
        }
    ):
        yield settings


@pytest.fixture
def settings_with_register_verification():
    with override_rest_registration_settings(
        {
            "REGISTER_VERIFICATION_ENABLED": True,
            "REGISTER_VERIFICATION_URL": REGISTER_VERIFICATION_URL,
            "VERIFICATION_FROM_EMAIL": VERIFICATION_FROM_EMAIL,
        }
    ):
        yield settings


@pytest.fixture
def settings_with_register_email_verification():
    with override_rest_registration_settings(
        {
            "REGISTER_EMAIL_VERIFICATION_ENABLED": True,
            "REGISTER_EMAIL_VERIFICATION_URL": REGISTER_EMAIL_VERIFICATION_URL,
            "VERIFICATION_FROM_EMAIL": VERIFICATION_FROM_EMAIL,
        }
    ):
        yield settings


@pytest.fixture
def settings_with_reset_password_verification():
    with override_rest_registration_settings(
        {
            "RESET_PASSWORD_VERIFICATION_ENABLED": True,
            "RESET_PASSWORD_VERIFICATION_URL": RESET_PASSWORD_VERIFICATION_URL,
            "VERIFICATION_FROM_EMAIL": VERIFICATION_FROM_EMAIL,
        }
    ):
        yield settings


@pytest.fixture
def settings_with_register_no_confirm():
    with override_rest_registration_settings(
        {
            "REGISTER_SERIALIZER_PASSWORD_CONFIRM": False,
        }
    ):
        yield settings


@pytest.fixture
def settings_with_reset_password_fail_when_user_not_found_disabled():
    with override_rest_registration_settings(
        {
            "RESET_PASSWORD_FAIL_WHEN_USER_NOT_FOUND": False,
        }
    ):
        yield settings


@pytest.fixture
def settings_with_simple_email_based_user():
    with override_auth_model_settings("custom_users.SimpleEmailBasedUser"):
        yield settings


@pytest.fixture
def settings_with_user_with_user_type():
    with override_auth_model_settings("custom_users.UserWithUserType"):
        yield settings


@pytest.fixture
def settings_with_user_with_unique_email():
    with override_auth_model_settings("custom_users.UserWithUniqueEmail"):
        yield settings


@pytest.fixture
def settings_with_user_with_channel():
    with override_auth_model_settings("custom_users.UserWithChannel"):
        yield settings


@pytest.fixture
def settings_with_coreapi_autoschema():
    with override_settings(
        REST_FRAMEWORK={
            "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",  # noqa: E501
        },
    ):
        yield settings


@pytest.fixture
def email_change():
    return StrValueChange(
        old_value="testuser1@example.com",
        new_value="testuser2@example.com",
    )


@pytest.fixture
def password_change():
    return StrValueChange(
        old_value=USER_PASSWORD,
        new_value="testpassword2",
    )


@pytest.fixture
def inactive_user(db, email_change, password_change):
    kwargs = {
        "email": email_change.old_value,
        "password": password_change.old_value,
        "is_active": False,
    }
    if settings.AUTH_USER_MODEL != "custom_users.SimpleEmailBasedUser":
        kwargs["username"] = USERNAME
    return create_test_user(**kwargs)


@pytest.fixture
def user(db, email_change, password_change):
    kwargs = {
        "email": email_change.old_value,
        "password": password_change.old_value,
    }
    if settings.AUTH_USER_MODEL != "custom_users.SimpleEmailBasedUser":
        kwargs["username"] = USERNAME
    return create_test_user(**kwargs)


@pytest.fixture
def user_token_obj(user):
    return Token.objects.create(user=user)


@pytest.fixture
def user2_with_user_email(db, email_change):
    return create_test_user(username=USERNAME2, email=email_change.old_value)


@pytest.fixture
def user2_with_user_new_email(db, email_change):
    return create_test_user(username=USERNAME2, email=email_change.new_value)


@pytest.fixture
def api_factory(api_view_provider):
    return APIViewRequestFactory(api_view_provider)


@pytest.fixture
def http_client():
    return Client()

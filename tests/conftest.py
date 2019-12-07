
import pytest
from django.conf import settings

from tests.helpers import (
    override_auth_model_settings,
    override_rest_registration_settings
)

REGISTER_VERIFICATION_URL = '/verify-account/'
VERIFICATION_FROM_EMAIL = 'no-reply@example.com'


@pytest.fixture()
def settings_minimal():
    yield settings


@pytest.fixture()
def settings_without_register_verification():
    with override_rest_registration_settings({
        'REGISTER_VERIFICATION_ENABLED': False,
    }):
        yield settings


@pytest.fixture()
def settings_with_register_verification():
    with override_rest_registration_settings({
        'REGISTER_VERIFICATION_ENABLED': True,
        'REGISTER_VERIFICATION_URL': REGISTER_VERIFICATION_URL,
        'VERIFICATION_FROM_EMAIL': VERIFICATION_FROM_EMAIL,
    }):
        yield settings


@pytest.fixture()
def settings_with_register_no_confirm():
    with override_rest_registration_settings({
        'REGISTER_SERIALIZER_PASSWORD_CONFIRM': False,
    }):
        yield settings


@pytest.fixture()
def settings_with_simple_email_based_user():
    with override_auth_model_settings('custom_users.SimpleEmailBasedUser'):
        yield settings

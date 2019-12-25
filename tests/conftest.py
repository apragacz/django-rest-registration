from collections import namedtuple

import pytest
from django.conf import settings

from tests.helpers.common import create_test_user
from tests.helpers.constants import (
    REGISTER_VERIFICATION_URL,
    RESET_PASSWORD_VERIFICATION_URL,
    VERIFICATION_FROM_EMAIL
)
from tests.helpers.settings import (
    override_auth_model_settings,
    override_rest_registration_settings
)

ValueChange = namedtuple('ValueChange', ['old_value', 'new_value'])


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
def settings_with_reset_password_verification():
    with override_rest_registration_settings({
        'RESET_PASSWORD_VERIFICATION_ENABLED': True,
        'RESET_PASSWORD_VERIFICATION_URL': RESET_PASSWORD_VERIFICATION_URL,
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
def settings_with_reset_password_fail_when_user_not_found_disabled():
    with override_rest_registration_settings({
        'RESET_PASSWORD_FAIL_WHEN_USER_NOT_FOUND': False,
    }):
        yield settings


@pytest.fixture()
def settings_with_simple_email_based_user():
    with override_auth_model_settings('custom_users.SimpleEmailBasedUser'):
        yield settings


@pytest.fixture()
def email_change():
    return ValueChange(
        old_value='testuser1@example.com',
        new_value='testuser2@example.com',
    )


@pytest.fixture()
def user(db, email_change):
    return create_test_user(
        username='testusername',
        email=email_change.old_value)


@pytest.fixture()
def user2_with_user_email(db, email_change):
    return create_test_user(
        username='testusername2',
        email=email_change.old_value)


@pytest.fixture()
def user2_with_user_new_email(db, email_change):
    return create_test_user(
        username='testusername2',
        email=email_change.new_value)

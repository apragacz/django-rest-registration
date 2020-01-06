import pytest
from rest_framework.authtoken.models import Token

from rest_registration.auth_token_managers import RestFrameworkAuthTokenManager
from rest_registration.exceptions import AuthTokenError


@pytest.fixture()
def auth_token_manager():
    return RestFrameworkAuthTokenManager()


def test_when_token_created_then_revoke_token_succeeds(
        user, user_token_obj, auth_token_manager):
    auth_token_manager.revoke_token(user)
    assert_token_keys_equals(user, [])


def test_when_no_token_then_revoke_token_fails(
        user, auth_token_manager):
    with pytest.raises(AuthTokenError):
        auth_token_manager.revoke_token(user)
    assert_token_keys_equals(user, [])


def test_when_token_created_then_revoke_token_fails_with_another_token(
        user, user_token_obj, auth_token_manager):
    token_key = user_token_obj.key
    another_token_key = token_key + 'x'
    with pytest.raises(AuthTokenError):
        auth_token_manager.revoke_token(user, token=another_token_key)
    assert_token_keys_equals(user, [token_key])


def assert_token_keys_equals(user, expected_token_keys):
    assert [
        t.key for t in Token.objects.filter(user=user)
    ] == expected_token_keys

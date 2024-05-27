import pytest
from django.test.utils import modify_settings, override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import force_authenticate

from tests.helpers.api_views import (
    assert_response_is_bad_request,
    assert_response_is_forbidden,
    assert_response_is_ok,
)
from tests.helpers.settings import override_rest_registration_settings
from tests.helpers.views import ViewProvider


def test_ok(settings_minimal, user, api_view_provider, api_factory):
    request = api_factory.create_post_request()
    api_factory.add_session_to_request(request)
    force_authenticate(request, user=user)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)


@override_rest_registration_settings(
    {
        "LOGIN_RETRIEVE_TOKEN": True,
    }
)
def test_ok_with_revoke_token(settings_minimal, user, api_view_provider, api_factory):
    _test_ok_with_revoke_token(
        user=user,
        api_view_provider=api_view_provider,
        api_factory=api_factory,
    )


@modify_settings(
    MIDDLEWARE={
        "remove": "django.contrib.sessions.middleware.SessionMiddleware",
    }
)
@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework.authentication.TokenAuthentication",
        ),
    },
)
def test_ok_with_revoke_token_without_session(
    settings_minimal, user, api_view_provider, api_factory
):
    _test_ok_with_revoke_token(
        user=user,
        api_view_provider=api_view_provider,
        api_factory=api_factory,
        add_session=False,
    )


def _test_ok_with_revoke_token(user, api_view_provider, api_factory, add_session=True):
    Token.objects.get_or_create(user=user)
    request = api_factory.create_post_request(
        {
            "revoke_token": True,
        }
    )
    if add_session:
        api_factory.add_session_to_request(request)
    force_authenticate(request, user=user)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert not Token.objects.filter(user=user).exists()


@override_rest_registration_settings(
    {
        "LOGIN_RETRIEVE_TOKEN": True,
    }
)
def test_fail_with_revoke_token_when_nonexistent_token(
    settings_minimal, user, api_view_provider, api_factory
):
    _test_fail_with_revoke_token_when_nonexistent_token(
        user=user,
        api_view_provider=api_view_provider,
        api_factory=api_factory,
    )


@modify_settings(
    MIDDLEWARE={
        "remove": "django.contrib.sessions.middleware.SessionMiddleware",
    }
)
@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "rest_framework.authentication.TokenAuthentication",
        ),
    },
)
def test_fail_with_revoke_token_when_nonexistent_token_without_session(
    settings_minimal, user, api_view_provider, api_factory
):
    _test_fail_with_revoke_token_when_nonexistent_token(
        user=user,
        api_view_provider=api_view_provider,
        api_factory=api_factory,
        add_session=False,
    )


def _test_fail_with_revoke_token_when_nonexistent_token(
    user, api_view_provider, api_factory, add_session=True
):
    assert not Token.objects.filter(user=user).exists()
    request = api_factory.create_post_request(
        {
            "revoke_token": True,
        }
    )
    if add_session:
        api_factory.add_session_to_request(request)
    force_authenticate(request, user=user)
    response = api_view_provider.view_func(request)
    assert_response_is_bad_request(response)


def test_fail_when_not_logged_in(
    settings_minimal, user, api_view_provider, api_factory
):
    request = api_factory.create_post_request()
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert_response_is_forbidden(response)


@override_rest_registration_settings(
    {
        "AUTH_TOKEN_MANAGER_CLASS": "tests.testapps.custom_authtokens.auth.FaultyAuthTokenManager",  # noqa: E501
        "LOGIN_RETRIEVE_TOKEN": True,
    }
)
def test_fail_when_faulty_auth_token_manager(
    settings_minimal,
    user,
    api_view_provider,
    api_factory,
):
    Token.objects.get_or_create(user=user)
    request = api_factory.create_post_request(
        {
            "revoke_token": True,
        }
    )
    force_authenticate(request, user=user)
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert_response_is_bad_request(response)
    assert response.data["detail"] == "Authentication token cannot be revoked"


@pytest.fixture
def api_view_provider():
    return ViewProvider("logout")

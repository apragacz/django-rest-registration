import django
import pytest
from rest_framework.authtoken.models import Token
from rest_framework.settings import api_settings
from rest_framework.test import APIRequestFactory

from tests.helpers.api_views import (
    assert_response_is_bad_request,
    assert_response_is_ok
)
from tests.helpers.settings import (
    override_rest_framework_settings,
    override_rest_registration_settings
)
from tests.helpers.views import ViewProvider
from tests.testapps.custom_authtokens.auth import JWTAuthentication

DJANGO_VERSION_INFO = tuple(int(s) for s in django.__version__.split("."))


def test_ok(
    settings_minimal,
    user, password_change, api_view_provider, api_factory,
    user_logged_in_send_mock, user_login_failed_send_mock,
):
    password = password_change.old_value
    request = api_factory.create_post_request({
        'login': user.username,
        'password': password,
    })
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    user_logged_in_send_mock.assert_called_once()
    user_login_failed_send_mock.assert_not_called()


@override_rest_registration_settings({
    'LOGIN_RETRIEVE_TOKEN': True,
})
def test_ok_with_session_and_token(
    settings_minimal,
    user, password_change, api_view_provider, api_factory,
    user_logged_in_send_mock, user_login_failed_send_mock,
):
    password = password_change.old_value
    request = api_factory.create_post_request({
        'login': user.username,
        'password': password,
    })
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert 'token' in response.data
    token_key = response.data['token']
    token = Token.objects.get(key=token_key)
    assert token.user == user
    user_logged_in_send_mock.assert_called_once()
    user_login_failed_send_mock.assert_not_called()


@override_rest_registration_settings({
    "LOGIN_RETRIEVE_TOKEN": True,
    "LOGIN_AUTHENTICATE_SESSION": False,
})
def test_ok_with_token_only(
    settings_minimal,
    user, password_change, api_view_provider, api_factory,
    user_logged_in_send_mock, user_login_failed_send_mock,
):
    password = password_change.old_value
    request = api_factory.create_post_request({
        "login": user.username,
        "password": password,
    })
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert "token" in response.data
    token_key = response.data["token"]
    token = Token.objects.get(key=token_key)
    assert token.user == user
    user_logged_in_send_mock.assert_called_once()
    user_login_failed_send_mock.assert_not_called()


def test_fail(
    settings_minimal,
    user, api_view_provider, api_factory,
    user_logged_in_send_mock, user_login_failed_send_mock,
):
    request = api_factory.create_post_request({
        'login': user.username,
        'password': 'blah',
    })
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert_response_is_bad_request(response)
    user_logged_in_send_mock.assert_not_called()
    user_login_failed_send_mock.assert_called_once()


@override_rest_registration_settings({
    'AUTH_TOKEN_MANAGER_CLASS': 'tests.testapps.custom_authtokens.auth.FaultyAuthTokenManager',  # noqa: E501
    'LOGIN_RETRIEVE_TOKEN': True,
})
def test_fail_when_faulty_auth_token_manager(
    settings_minimal,
    user, password_change, api_view_provider, api_factory,
    user_logged_in_send_mock, user_login_failed_send_mock,
):
    password = password_change.old_value
    request = api_factory.create_post_request({
        'login': user.username,
        'password': password,
    })
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert_response_is_bad_request(response)
    user_logged_in_send_mock.assert_not_called()
    user_login_failed_send_mock.assert_called_once()


@override_rest_registration_settings({
    'USE_NON_FIELD_ERRORS_KEY_FROM_DRF_SETTINGS': True,
})
def test_fail_with_invalid_non_field_errors(
    settings_minimal,
    user, password_change, api_view_provider, api_factory,
    user_logged_in_send_mock, user_login_failed_send_mock,
):
    request = api_factory.create_post_request({
        'login': user.username,
        'password': "blah",
    })
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert "non_field_errors" in response.data
    assert_response_is_bad_request(response)
    user_logged_in_send_mock.assert_not_called()
    user_login_failed_send_mock.assert_called_once()


@override_rest_registration_settings({
    'USER_LOGIN_FIELDS': ['username', 'email'],
})
def test_ok_when_user_with_unique_email_logs_with_username(
    settings_minimal, settings_with_user_with_unique_email,
    user, password_change, api_view_provider, api_factory,
    user_logged_in_send_mock, user_login_failed_send_mock,
):
    password = password_change.old_value
    request = api_factory.create_post_request({
        'login': user.username,
        'password': password,
    })
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    user_logged_in_send_mock.assert_called_once()
    user_login_failed_send_mock.assert_not_called()


@override_rest_registration_settings({
    'USER_LOGIN_FIELDS': ['username', 'email'],
})
def test_ok_when_user_with_unique_email_logs_with_email(
    settings_minimal, settings_with_user_with_unique_email,
    user, password_change, api_view_provider, api_factory,
    user_logged_in_send_mock, user_login_failed_send_mock,
):
    password = password_change.old_value
    request = api_factory.create_post_request({
        'login': user.email,
        'password': password,
    })
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    user_logged_in_send_mock.assert_called_once()
    # Unfortunately, due to the fact that
    # django.contrib.auth.authenticate() will send user_login_failed signal
    # during the first "try" (with "username" field), and the second one
    # will actually succeed; the line:
    #   user_login_failed_send_mock.assert_not_called()
    # needs to be replaced with the one below:
    user_login_failed_send_mock.assert_called_once()


@pytest.mark.skipif(
    DJANGO_VERSION_INFO < (5, 0),
    reason="requires Django 5.0 or higher",
)
@override_rest_registration_settings({
    'AUTH_TOKEN_MANAGER_CLASS': 'tests.testapps.custom_authtokens.auth.AuthJWTManager',
    'LOGIN_RETRIEVE_TOKEN': True,
})
@override_rest_framework_settings({
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'tests.testapps.custom_authtokens.auth.JWTAuthentication',
    ),
})
def test_ok_with_token_and_auth_jwt_manager(
    settings_minimal,
    user, password_change, api_view_provider, api_factory,
):
    assert api_settings.DEFAULT_AUTHENTICATION_CLASSES == [JWTAuthentication]
    password = password_change.old_value
    request = api_factory.create_post_request({
        'login': user.username,
        'password': password,
    })
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)
    assert 'token' in response.data
    token_key = response.data['token']

    # test sample endpoint requiring authentication
    profile_view_provider = ViewProvider('profile')
    api_request_factory = APIRequestFactory()
    authorized_request = api_request_factory.get(
        profile_view_provider.view_url,
        headers={
            'Authorization': f"Bearer {token_key}",
        },
    )
    response = profile_view_provider.view_func(authorized_request)
    assert_response_is_ok(response)


@pytest.fixture()
def api_view_provider():
    return ViewProvider('login')

import pytest
from django.middleware.csrf import get_token
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.authtoken.models import Token

from tests.helpers.api_views import (
    APIViewRequestFactory,
    assert_response_is_bad_request,
    assert_response_is_ok,
    assert_response_status_is_forbidden
)
from tests.helpers.settings import (
    override_rest_framework_settings_dict,
    override_rest_registration_settings
)
from tests.helpers.views import ViewProvider

from ..base import APIViewTestCase


class LoginViewTestCase(APIViewTestCase):
    VIEW_NAME = 'login'

    def setUp(self):
        super().setUp()
        self.password = 'testpassword'
        self.user = self.create_test_user(password=self.password)

    def test_success(self):
        request = self.create_post_request({
            'login': self.user.username,
            'password': self.password,
        })
        self.add_session_to_request(request)
        response = self.view_func(request)
        self.assert_valid_response(response, status.HTTP_200_OK)

    @override_settings(
        REST_REGISTRATION={
            'LOGIN_RETRIEVE_TOKEN': True,
        },
    )
    def test_success_with_token(self):
        request = self.create_post_request({
            'login': self.user.username,
            'password': self.password,
        })
        self.add_session_to_request(request)
        response = self.view_func(request)
        self.assert_valid_response(response, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        token_key = response.data['token']
        token = Token.objects.get(key=token_key)
        self.assertEqual(token.user, self.user)

    def test_invalid(self):
        request = self.create_post_request({
            'login': self.user.username,
            'password': 'blah',
        })
        self.add_session_to_request(request)
        response = self.view_func(request)
        self.assert_invalid_response(response, status.HTTP_400_BAD_REQUEST)


@pytest.fixture()
def api_view_provider():
    return ViewProvider('login')


@override_rest_registration_settings({
    'AUTH_TOKEN_MANAGER_CLASS': 'tests.testapps.custom_authtokens.auth.FaultyAuthTokenManager',  # noqa: E501
    'LOGIN_RETRIEVE_TOKEN': True,
})
def test_when_faulty_auth_token_manager_then_login_fails(
        settings_minimal,
        user, password_change, api_view_provider, api_factory):
    password = password_change.old_value
    request = api_factory.create_post_request({
        'login': user.username,
        'password': password,
    })
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert_response_is_bad_request(response)


@override_rest_registration_settings({
    'USE_NON_FIELD_ERRORS_KEY_FROM_DRF_SETTINGS': True,
})
def test_invalid_non_field_errors(
        settings_minimal,
        user, password_change, api_view_provider, api_factory):
    request = api_factory.create_post_request({
        'login': user.username,
        'password': "blah",
    })
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert "non_field_errors" in response.data
    assert_response_is_bad_request(response)


@override_rest_registration_settings({
    'LOGIN_SERIALIZER_CLASS': 'tests.testapps.custom_serializers.serializers.DefaultDeprecatedLoginSerializer',  # noqa: E501
})
def test_when_deprecated_login_serializer_then_success(
        settings_minimal, user,
        api_view_provider, api_factory):
    request = api_factory.create_post_request({
        'login': 'abra',
        'password': 'cadabra',
    })
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)


# TODO: Issue #114 - remove code testing support of deprecated behavior
@override_rest_registration_settings({
    'LOGIN_SERIALIZER_CLASS': 'tests.testapps.custom_serializers.serializers.DefaultDeprecatedLoginSerializer',  # noqa: E501
})
def test_when_deprecated_login_serializer_and_invalid_creds_then_failure(
        settings_minimal, user,
        api_view_provider, api_factory):
    request = api_factory.create_post_request({
        'login': 'abra',
        'password': 'blabla',
    })
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert_response_is_bad_request(response)


@override_rest_registration_settings({
    'USER_LOGIN_FIELDS': ['username', 'email'],
})
def test_ok_when_user_with_unique_email_logs_with_username(
        settings_minimal, settings_with_user_with_unique_email,
        user, password_change, api_view_provider, api_factory):
    password = password_change.old_value
    request = api_factory.create_post_request({
        'login': user.username,
        'password': password,
    })
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)


@override_rest_registration_settings({
    'USER_LOGIN_FIELDS': ['username', 'email'],
})
def test_ok_when_user_with_unique_email_logs_with_email(
        settings_minimal, settings_with_user_with_unique_email,
        user, password_change, api_view_provider, api_factory):
    password = password_change.old_value
    request = api_factory.create_post_request({
        'login': user.email,
        'password': password,
    })
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)


@override_rest_framework_settings_dict({
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_registration.api.authentication.SessionCSRFAuthentication',
    ],
})
def test_fail_with_csrf_enabled_and_missing_token(
    settings_minimal,
    user, password_change,
    api_view_provider,
):
    password = password_change.old_value
    api_factory = APIViewRequestFactory(api_view_provider, enforce_csrf_checks=True)
    request = api_factory.create_post_request({
        'login': user.username,
        'password': password,
    })
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert_response_status_is_forbidden(response)


# TODO: fix this test
@override_rest_framework_settings_dict({
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_registration.api.authentication.SessionCSRFAuthentication',
    ],
})
def test_ok_with_csrf_enabled(
    settings_minimal,
    user, password_change,
    api_view_provider,
):
    password = password_change.old_value
    api_factory = APIViewRequestFactory(api_view_provider, enforce_csrf_checks=True)
    request = api_factory.create_post_request({
        'login': user.username,
        'password': password,
    })
    csrf_token = get_token(request)
    api_factory.add_session_to_request(request)
    response = api_view_provider.view_func(request)
    assert_response_is_ok(response)

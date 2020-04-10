import pytest
from django.test.utils import override_settings
from rest_framework import status
from rest_framework.authtoken.models import Token

from tests.helpers.api_views import assert_response_is_bad_request
from tests.helpers.settings import override_rest_registration_settings
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

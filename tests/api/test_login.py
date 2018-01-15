from django.test.utils import override_settings
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import force_authenticate

from rest_registration.api.views import login, logout

from .base import APIViewTestCase


class BaseLoginTestCase(APIViewTestCase):

    def setUp(self):
        super().setUp()
        self.password = 'testpassword'
        self.user = self.create_test_user(password=self.password)


class LoginViewTestCase(BaseLoginTestCase):

    def test_success(self):
        request = self.factory.post('', {
            'login': self.user.username,
            'password': self.password,
        })
        self.add_session_to_request(request)
        response = login(request)
        self.assert_valid_response(response, status.HTTP_200_OK)

    @override_settings(
        REST_REGISTRATION={
            'LOGIN_RETRIEVE_TOKEN': True,
        },
    )
    def test_success_with_token(self):
        request = self.factory.post('', {
            'login': self.user.username,
            'password': self.password,
        })
        self.add_session_to_request(request)
        response = login(request)
        self.assert_valid_response(response, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        token_key = response.data['token']
        token = Token.objects.get(key=token_key)
        self.assertEqual(token.user, self.user)

    def test_invalid(self):
        request = self.factory.post('', {
            'login': self.user.username,
            'password': 'blah',
        })
        self.add_session_to_request(request)
        response = login(request)
        self.assert_invalid_response(response, status.HTTP_400_BAD_REQUEST)


class LogoutViewTestCase(BaseLoginTestCase):

    def test_success(self):
        request = self.factory.post('')
        self.add_session_to_request(request)
        force_authenticate(request, user=self.user)
        response = logout(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_not_logged_in(self):
        request = self.factory.post('')
        self.add_session_to_request(request)
        response = logout(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

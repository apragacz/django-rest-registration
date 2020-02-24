from django.test.utils import modify_settings, override_settings
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import force_authenticate

from ..base import APIViewTestCase


class LogoutViewTestCase(APIViewTestCase):
    VIEW_NAME = 'logout'

    def setUp(self):
        super().setUp()
        self.password = 'testpassword'
        self.user = self.create_test_user(password=self.password)

    def test_success(self):
        request = self.create_post_request()
        self.add_session_to_request(request)
        force_authenticate(request, user=self.user)
        response = self.view_func(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @override_settings(
        REST_REGISTRATION={
            'LOGIN_RETRIEVE_TOKEN': True,
        },
    )
    def test_revoke_token_success(self):
        self._test_revoke_token_success()

    @modify_settings(
        MIDDLEWARE={
            'remove': 'django.contrib.sessions.middleware.SessionMiddleware',
        }
    )
    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'rest_framework.authentication.TokenAuthentication',
            ),
        },
    )
    def test_revoke_token_success_without_session(self):
        self._test_revoke_token_success(add_session=False)

    def _test_revoke_token_success(self, add_session=True):
        Token.objects.get_or_create(user=self.user)
        request = self.create_post_request({
            'revoke_token': True,
        })
        if add_session:
            self.add_session_to_request(request)
        force_authenticate(request, user=self.user)
        response = self.view_func(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(user=self.user).exists())

    @override_settings(
        REST_REGISTRATION={
            'LOGIN_RETRIEVE_TOKEN': True,
        },
    )
    def test_revoke_nonexistent_token_failure(self):
        self._test_revoke_nonexistent_token_failure()

    @modify_settings(
        MIDDLEWARE={
            'remove': 'django.contrib.sessions.middleware.SessionMiddleware',
        }
    )
    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'rest_framework.authentication.TokenAuthentication',
            ),
        },
    )
    def test_revoke_nonexistent_token_failure_without_session(self):
        self._test_revoke_nonexistent_token_failure(add_session=False)

    def _test_revoke_nonexistent_token_failure(self, add_session=True):
        self.assertFalse(Token.objects.filter(user=self.user).exists())
        request = self.create_post_request({
            'revoke_token': True,
        })
        if add_session:
            self.add_session_to_request(request)
        force_authenticate(request, user=self.user)
        response = self.view_func(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_logged_in(self):
        request = self.create_post_request()
        self.add_session_to_request(request)
        response = self.view_func(request)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

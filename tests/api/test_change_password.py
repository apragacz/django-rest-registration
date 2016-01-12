from rest_framework import status
from rest_framework.test import force_authenticate

from rest_registration.api.change_password_views import change_password
from .base import APIViewTestCase


class ChangePasswordTestCase(APIViewTestCase):

    def setUp(self):
        super().setUp()
        self.password = 'testpassword'
        self.user = self.create_test_user(password=self.password)

    def test_forbidden(self):
        request = self.factory.post('', {})
        response = change_password(request)
        self.assert_invalid_response(response, status.HTTP_403_FORBIDDEN)

    def _test_authenticated(self, data):
        old_password = 'testpassword'
        user = self.create_test_user(password=old_password)
        request = self.factory.post('', data)
        force_authenticate(request, user=user)
        response = change_password(request)
        return response

    def test_invalid_old_password(self):
        new_password = 'newtestpassword'
        response = self._test_authenticated({
            'old_password': 'blah',
            'password': new_password,
            'password_confirm': new_password,
        })
        self.assert_invalid_response(response, status.HTTP_400_BAD_REQUEST)

    def test_invalid_confirm(self):
        new_password = 'newtestpassword'
        response = self._test_authenticated({
            'old_password': self.password,
            'password': new_password,
            'password_confirm': new_password + 'a',
        })
        self.assert_invalid_response(response, status.HTTP_400_BAD_REQUEST)

    def test_ok(self):
        new_password = 'newtestpassword'
        response = self._test_authenticated({
            'old_password': self.password,
            'password': new_password,
            'password_confirm': new_password,
        })
        self.assert_valid_response(response, status.HTTP_200_OK)

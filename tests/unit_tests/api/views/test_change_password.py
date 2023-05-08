from django.test.utils import override_settings
from rest_framework import status
from rest_framework.test import force_authenticate

from .base import APIViewTestCase


class _BaseChangePasswordTestCase(APIViewTestCase):
    VIEW_NAME = 'change-password'

    def setUp(self):
        super().setUp()
        self.password = 'testpassword'
        self.user = self.create_test_user(username='albert.einstein',
                                          password=self.password)

    def test_forbidden(self):
        request = self.create_post_request({})
        response = self.view_func(request)
        self.assert_invalid_response(response, status.HTTP_403_FORBIDDEN)

    def _test_authenticated(self, data):
        request = self.create_post_request(data)
        force_authenticate(request, user=self.user)
        response = self.view_func(request)
        return response


class ChangePasswordTestCase(_BaseChangePasswordTestCase):

    def test_invalid_old_password(self):
        new_password = 'newtestpassword'
        response = self._test_authenticated({
            'old_password': 'blah',
            'password': new_password,
            'password_confirm': new_password,
        })
        self.assert_response_is_bad_request(response)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.password))

    def test_missing_confirm(self):
        new_password = 'newtestpassword'
        response = self._test_authenticated({
            'old_password': self.password,
            'password': new_password,
        })
        self.assert_response_is_bad_request(response)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.password))

    def test_invalid_confirm(self):
        new_password = 'newtestpassword'
        response = self._test_authenticated({
            'old_password': self.password,
            'password': new_password,
            'password_confirm': new_password + 'a',
        })
        self.assert_response_is_bad_request(response)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.password))

    def test_short_password(self):
        new_password = 'a'
        response = self._test_authenticated({
            'old_password': self.password,
            'password': new_password,
            'password_confirm': new_password,
        })
        self.assert_response_is_bad_request(response)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.password))

    def test_numeric_password(self):
        new_password = '234665473425345'
        response = self._test_authenticated({
            'old_password': self.password,
            'password': new_password,
            'password_confirm': new_password,
        })
        self.assert_response_is_bad_request(response)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.password))

    def test_password_same_as_username(self):
        new_password = self.user.username
        response = self._test_authenticated({
            'old_password': self.password,
            'password': new_password,
            'password_confirm': new_password,
        })
        self.assert_response_is_bad_request(response)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.password))

    def test_ok(self):
        new_password = 'newtestpassword'
        response = self._test_authenticated({
            'old_password': self.password,
            'password': new_password,
            'password_confirm': new_password,
        })
        self.assert_response_is_ok(response)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))


@override_settings(
    REST_REGISTRATION={
        'CHANGE_PASSWORD_SERIALIZER_PASSWORD_CONFIRM': False,
    }
)
class ChangePasswordWithoutConfirmTestCase(_BaseChangePasswordTestCase):

    def test_short_password(self):
        new_password = 'a'
        response = self._test_authenticated({
            'old_password': self.password,
            'password': new_password,
        })
        self.assert_response_is_bad_request(response)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.password))

    def test_numeric_password(self):
        new_password = '234665473425345'
        response = self._test_authenticated({
            'old_password': self.password,
            'password': new_password,
        })
        self.assert_response_is_bad_request(response)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.password))

    def test_password_same_as_username(self):
        new_password = self.user.username
        response = self._test_authenticated({
            'old_password': self.password,
            'password': new_password,
        })
        self.assert_response_is_bad_request(response)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.password))

    def test_ok(self):
        new_password = 'newtestpassword'
        response = self._test_authenticated({
            'old_password': self.password,
            'password': new_password,
        })
        self.assert_response_is_ok(response)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))

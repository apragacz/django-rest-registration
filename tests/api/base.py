import contextlib

from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail
from django.test import TestCase
from django_dynamic_fixture import G
from rest_framework.test import APIRequestFactory

from rest_registration.utils import get_user_model_class


class APIViewTestCase(TestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user_class = get_user_model_class()

    def create_test_user(self, **kwargs):
        password = kwargs.pop('password', None)
        user = G(self.user_class, **kwargs)
        if password is not None:
            user.set_password(password)
            user.save()
            user.password_in_plaintext = password
        return user

    def add_session_to_request(self, request):
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()

    def assert_response(self, response, valid=True, expected_status_code=None):
        status_code = response.status_code
        status_valid = (200 <= status_code < 400)
        msg = 'Response returned with code {}, body {}'.format(
            status_code,
            response.data,
        )
        if valid:
            self.assertTrue(status_valid, msg)
        else:
            self.assertFalse(status_valid, msg)

        if status_code is not None:
            self.assertEqual(status_code, expected_status_code, msg)

    def assert_valid_response(self, response, expected_status_code=None):
        self.assert_response(response, valid=True,
                             expected_status_code=expected_status_code)

    def assert_invalid_response(self, response, expected_status_code=None):
        self.assert_response(response, valid=False,
                             expected_status_code=expected_status_code)

    def _assert_mails_sent(self, count):
        before = len(mail.outbox)
        yield
        after = len(mail.outbox)
        self.assertEqual(after, before + count)

    @contextlib.contextmanager
    def assert_mails_sent(self, count):
        yield from self._assert_mails_sent(count)

    @contextlib.contextmanager
    def assert_mail_sent(self):
        yield from self._assert_mails_sent(1)

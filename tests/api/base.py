import contextlib
from collections import Sequence

from django.contrib.sessions.middleware import SessionMiddleware
from django.core import mail
from django.test import TestCase
from django_dynamic_fixture import G
from rest_framework import status
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

        if expected_status_code is not None:
            self.assertEqual(status_code, expected_status_code, msg)

    def assert_valid_response(self, response, expected_status_code=None):
        self.assert_response(response, valid=True,
                             expected_status_code=expected_status_code)

    def assert_invalid_response(self, response, expected_status_code=None):
        self.assert_response(response, valid=False,
                             expected_status_code=expected_status_code)

    def assert_response_is_ok(self, response):
        self.assert_valid_response(
            response,
            expected_status_code=status.HTTP_200_OK,
        )

    def assert_response_is_bad_request(self, response):
        self.assert_invalid_response(
            response,
            expected_status_code=status.HTTP_400_BAD_REQUEST,
        )

    @contextlib.contextmanager
    def _assert_mails_sent(self, count):
        before = len(mail.outbox)
        sent_emails = EmailMessageContainer()
        yield sent_emails
        sent_emails.set(mail.outbox[before:])
        after = len(mail.outbox)
        self.assertEqual(after, before + count)

    @contextlib.contextmanager
    def assert_mails_sent(self, count):
        with self._assert_mails_sent(count) as sent_emails:
            yield sent_emails

    @contextlib.contextmanager
    def assert_one_mail_sent(self):
        with self._assert_mails_sent(1) as sent_emails:
            yield sent_emails

    @contextlib.contextmanager
    def assert_no_mail_sent(self):
        with self._assert_mails_sent(0) as sent_emails:
            yield sent_emails


class EmailMessageContainer(Sequence):

    def __init__(self):
        self._mails = []
        self._set = False

    def __len__(self):
        return len(self._mails)

    def __getitem__(self, i):
        return self._mails[i]

    def set(self, mails):
        assert not self._set
        self._mails = list(mails)
        self._set = True

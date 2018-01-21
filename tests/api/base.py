import contextlib
from collections import Sequence
from urllib.parse import parse_qs, urlparse

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

    def assert_len_equals(self, collection, expected_len):
        msg_format = "{collection} does not have length {expected_len}"
        msg = msg_format.format(
            collection=collection,
            expected_len=expected_len,
        )
        self.assertEqual(len(collection), expected_len, msg=msg)

    def assert_response(
            self, response, expected_valid_response=True,
            expected_status_code=None):
        status_code = response.status_code
        status_valid = (200 <= status_code < 400)
        msg_format = "Response returned with code {status_code}, body {response.data}"  # noqa: E501
        msg = msg_format.format(
                status_code=status_code,
                response=response)
        if expected_valid_response:
            self.assertTrue(status_valid, msg)
        else:
            self.assertFalse(status_valid, msg)

        if expected_status_code is not None:
            self.assertEqual(status_code, expected_status_code, msg)

    def assert_valid_response(self, response, expected_status_code=None):
        self.assert_response(
            response,
            expected_valid_response=True,
            expected_status_code=expected_status_code)

    def assert_invalid_response(self, response, expected_status_code=None):
        self.assert_response(
            response,
            expected_valid_response=False,
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
    def _assert_mails_sent(self, expected_num):
        before = len(mail.outbox)
        sent_emails = EmailMessageContainer()
        yield sent_emails
        sent_emails.set(mail.outbox[before:])
        after = len(mail.outbox)
        num_of_sent_emails = after - before

        msg_format = "Expected {expected_num} emails to be sent, but found {num_of_sent_emails}"  # noqa: E501
        msg = msg_format.format(
            expected_num=expected_num,
            num_of_sent_emails=num_of_sent_emails,
        )
        self.assertEqual(num_of_sent_emails, expected_num, msg=msg)

    @contextlib.contextmanager
    def assert_mails_sent(self, expected_num):
        with self._assert_mails_sent(expected_num) as sent_emails:
            yield sent_emails

    @contextlib.contextmanager
    def assert_one_mail_sent(self):
        with self._assert_mails_sent(1) as sent_emails:
            yield sent_emails

    @contextlib.contextmanager
    def assert_no_mail_sent(self):
        with self._assert_mails_sent(0) as sent_emails:
            yield sent_emails

    def _assert_url_lines_in_text(self, text, expected_num):
        lines = [line.rstrip() for line in text.split('\n')]
        url_lines = [
            line for line in lines
            if line.startswith('http://') or line.startswith('https://')
        ]
        num_of_url_lines = len(url_lines)
        msg_format = "Found {num_of_url_lines} url lines instead of {expected_num} in:\n{text}"  # noqa: E501
        msg = msg_format.format(
            num_of_url_lines=num_of_url_lines,
            expected_num=expected_num,
            text=text,
        )
        self.assertEqual(num_of_url_lines, expected_num, msg=msg)
        return url_lines

    def assert_one_url_line_in_text(self, text):
        url_lines = self._assert_url_lines_in_text(text, 1)
        return url_lines[0]

    def assert_valid_verification_url(
            self, url, expected_path=None, expected_query_keys=None):
        parsed_url = urlparse(url)
        if expected_path is not None:
            self.assertEqual(parsed_url.path, expected_path)
        query = parse_qs(parsed_url.query, strict_parsing=True)
        if expected_query_keys is not None:
            self.assertSetEqual(set(query), set(expected_query_keys))

        for values in query.values():
            self.assert_len_equals(values, 1)

        verification_data = {key: values[0] for key, values in query.items()}
        return verification_data


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

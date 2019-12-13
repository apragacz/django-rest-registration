import contextlib
import re

from django.contrib.auth import get_user_model
from django.test import TestCase as DjangoTestCase
from django.urls import reverse

from rest_registration.verification import get_current_timestamp

from .common import create_test_user
from .email import capture_sent_emails
from .timer import capture_time


class TestCase(DjangoTestCase):

    @property
    def user_class(self):
        # Ensure that the user class is always fresh
        # for instance, in case of settings override.
        return get_user_model()

    def create_test_user(self, **kwargs):
        return create_test_user(**kwargs)

    def assert_len_equals(self, collection, expected_len, msg=None):
        std_msg_format = "{collection} does not have length {expected_len}"
        std_msg = std_msg_format.format(
            collection=collection,
            expected_len=expected_len,
        )
        if len(collection) != expected_len:
            self.fail(self._formatMessage(msg, std_msg))

    def assert_is_between(self, value, start, end, msg=None):
        std_msg_format = "{value} is not in range [{start}, {end})"
        std_msg = std_msg_format.format(
            value=value,
            start=start,
            end=end,
        )
        if not start <= value < end:
            self.fail(self._formatMessage(msg, std_msg))

    def assert_is_not_between(self, value, start, end, msg=None):
        std_msg_format = "{value} is unexpectedly in range [{start}, {end})"
        std_msg = std_msg_format.format(
            value=value,
            start=start,
            end=end,
        )
        if start <= value < end:
            self.fail(self._formatMessage(msg, std_msg))

    @contextlib.contextmanager
    def capture_sent_emails(self):
        with capture_sent_emails() as emails:
            yield emails

    @contextlib.contextmanager
    def _assert_mails_sent(self, expected_num):
        with self.capture_sent_emails() as sent_emails:
            yield sent_emails
        num_of_sent_emails = len(sent_emails)
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

    @contextlib.contextmanager
    def timer(self, current_timestamp_getter=get_current_timestamp):
        with capture_time(
                current_timestamp_getter=current_timestamp_getter) as timer:
            yield timer

    def _assert_urls_in_text(self, text, expected_num, line_url_pattern):
        lines = [line.rstrip() for line in text.split('\n')]
        urls = []
        for line in lines:
            for match in re.finditer(line_url_pattern, line):
                match_groupdict = match.groupdict()
                urls.append(match_groupdict['url'])
        num_of_urls = len(urls)
        msg_format = "Found {num_of_urls} urls instead of {expected_num} in:\n{text}"  # noqa: E501
        msg = msg_format.format(
            num_of_urls=num_of_urls,
            expected_num=expected_num,
            text=text,
        )
        self.assertEqual(num_of_urls, expected_num, msg=msg)
        return urls

    def assert_no_url_in_text(self, text):
        self._assert_urls_in_text(text, 0, r'https?://.*')

    def assert_one_url_line_in_text(self, text):
        url_lines = self._assert_urls_in_text(
            text, 1, r'^(?P<url>https?://.*)$')
        return url_lines[0]

    def assert_one_url_in_brackets_in_text(self, text):
        urls = self._assert_urls_in_text(
            text, 1, r'\((?P<url>https?://.*)\)')
        return urls[0]


class BaseViewTestCase(TestCase):
    APP_NAME = None
    VIEW_NAME = None

    def setUp(self):
        super().setUp()
        self._view_url = None

    @property
    def full_view_name(self):
        assert self.APP_NAME
        assert self.VIEW_NAME
        return '{self.APP_NAME}:{self.VIEW_NAME}'.format(self=self)

    @property
    def view_url(self):
        if self._view_url is None:
            self._view_url = reverse(self.full_view_name)
        return self._view_url

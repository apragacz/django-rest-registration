import contextlib
from collections.abc import Sequence

from django.core import mail


def assert_one_email_sent(sent_emails):
    _assert_emails_sent(sent_emails, 1)
    return sent_emails[0]


def assert_no_email_sent(sent_emails):
    _assert_emails_sent(sent_emails, 0)


@contextlib.contextmanager
def capture_sent_emails():
    sent_emails = EmailMessageContainer()
    try:
        before = len(mail.outbox)
        yield sent_emails
        sent_emails.set(mail.outbox[before:])
    finally:
        if not sent_emails.is_set():
            sent_emails.set([])


class EmailMessageContainer(Sequence):

    def __init__(self):
        super().__init__()
        self._mails = []
        self._is_set = False

    def __len__(self):
        return len(self._mails)

    def __getitem__(self, i):
        return self._mails[i]

    def set(self, mails):
        assert not self._is_set
        self._mails = list(mails)
        self._is_set = True

    def is_set(self):
        return self._is_set


def _assert_emails_sent(sent_emails, expected_num):
    num_of_sent_emails = len(sent_emails)
    msg_format = "Expected {expected_num} emails to be sent, but found {num_of_sent_emails}"  # noqa: E501
    msg = msg_format.format(
        expected_num=expected_num,
        num_of_sent_emails=num_of_sent_emails,
    )
    assert num_of_sent_emails == expected_num, msg

from unittest import mock

import pytest
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed
)


@pytest.fixture()
def user_logged_in_send_mock(monkeypatch):
    return _mock_signal_send(monkeypatch, user_logged_in)


@pytest.fixture()
def user_logged_out_send_mock(monkeypatch):
    return _mock_signal_send(monkeypatch, user_logged_out)


@pytest.fixture()
def user_login_failed_send_mock(monkeypatch):
    return _mock_signal_send(monkeypatch, user_login_failed)


def _mock_signal_send(monkeypatch, sig):
    fmock = mock.Mock()
    monkeypatch.setattr(sig, "send", fmock)
    return fmock

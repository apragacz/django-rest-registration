import datetime
import time
from unittest.mock import patch
from urllib.parse import urlencode

import pytest
from django.core.signing import BadSignature, SignatureExpired

from rest_registration.utils.signers import DataSigner, URLParamsSigner


class ExampleSigner(DataSigner):
    pass


class ExampleTimestampSigner(DataSigner):
    USE_TIMESTAMP = True
    VALID_PERIOD = datetime.timedelta(days=1)


class ExampleURLSigner(URLParamsSigner):
    BASE_URL = "/verify/"
    USE_TIMESTAMP = True
    VALID_PERIOD = datetime.timedelta(days=1)


SIGNER_CLASSES = [ExampleSigner, ExampleTimestampSigner, ExampleURLSigner]


@pytest.mark.parametrize(
    "signer_cls", SIGNER_CLASSES,
)
def test_verify_ok(
    signer_cls, unsigned_data,
):
    signer = signer_cls(unsigned_data)
    signed_data = signer.get_signed_data()
    verify_signer = signer_cls(signed_data)
    verify_signer.verify()


@pytest.mark.parametrize(
    "signer_cls", SIGNER_CLASSES,
)
def test_verify_tamper_email_fail(
    signer_cls, unsigned_data,
):
    signer = signer_cls(unsigned_data)
    signed_data = signer.get_signed_data()
    signed_data["email"] = "a" + signed_data["email"]
    verify_signer = signer_cls(signed_data)

    with pytest.raises(BadSignature):
        verify_signer.verify()


@pytest.mark.parametrize(
    "signer_cls", SIGNER_CLASSES,
)
def test_verify_tamper_signature_fail(
    signer_cls, unsigned_data,
):
    signer = signer_cls(unsigned_data)
    signed_data = signer.get_signed_data()
    sig_field = DataSigner.SIGNATURE_FIELD
    signed_data[sig_field] = "a" + signed_data[sig_field]
    verify_signer = signer_cls(signed_data)

    with pytest.raises(BadSignature):
        verify_signer.verify()


@pytest.mark.parametrize(
    "signer_cls", SIGNER_CLASSES,
)
def test_verify_missing_singature_fail(
    signer_cls, unsigned_data,
):
    signer = signer_cls(unsigned_data)
    with pytest.raises(BadSignature):
        signer.verify()


def test_verify_missing_timestamp(unsigned_data):
    signer_cls = ExampleTimestampSigner
    timestamp = int(time.time())
    with patch("time.time", side_effect=lambda: timestamp):
        signer = signer_cls(unsigned_data)
    signed_data = signer.get_signed_data()
    del signed_data["timestamp"]
    with patch("time.time", side_effect=lambda: timestamp + 1):
        verify_signer = signer_cls(signed_data)
        with pytest.raises(BadSignature):
            verify_signer.verify()


def test_verify_expired(unsigned_data):
    signer_cls = ExampleTimestampSigner
    timestamp = int(time.time())
    with patch("time.time", side_effect=lambda: timestamp):
        signer = signer_cls(unsigned_data)
        signed_data = signer.get_signed_data()
    with patch("time.time", side_effect=lambda: timestamp + 3600 * 24 * 2):
        verify_signer = signer_cls(signed_data)
        with pytest.raises(SignatureExpired):
            verify_signer.verify()


def test_get_url(unsigned_data, unsigned_data_email):
    signer_cls = ExampleURLSigner
    signer = signer_cls(unsigned_data)
    url = signer.get_url()
    assert signer_cls.BASE_URL in url
    assert urlencode({"email": unsigned_data_email}) in url


@pytest.fixture
def unsigned_data(unsigned_data_email):
    return {
        "email": unsigned_data_email,
    }


@pytest.fixture
def unsigned_data_email():
    return "test@example.com"

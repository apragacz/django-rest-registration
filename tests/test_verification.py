import datetime
import time
from unittest.mock import patch
from urllib.parse import urlencode

from django.core.signing import BadSignature, SignatureExpired
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from rest_registration.verification import DataSigner, URLParamsSigner


class ExampleSigner(DataSigner):
    pass


class ExampleTimestampSigner(DataSigner):
    USE_TIMESTAMP = True
    VALID_PERIOD = datetime.timedelta(days=1)


class ExampleURLSigner(URLParamsSigner):
    BASE_URL = '/verify/'
    USE_TIMESTAMP = True
    VALID_PERIOD = datetime.timedelta(days=1)


class BaseTestSignerMixin(object):
    cls = None
    test_email = 'test@example.com'

    def create_signer(self, data):
        return self.cls(data)  # pylint: disable=E1102

    def test_verify_ok(self):
        signer1 = self.create_signer({
            'email': self.test_email,
        })
        signed_data = signer1.get_signed_data()
        signer2 = self.create_signer(signed_data)
        signer2.verify()
        signer2.verify()

    def test_verify_tamper_email(self):
        signer1 = self.create_signer({
            'email': self.test_email,
        })
        signed_data = signer1.get_signed_data()
        signed_data['email'] = 'a' + signed_data['email']
        signer2 = self.create_signer(signed_data)
        self.assertRaises(BadSignature, signer2.verify)

    def test_verify_missing_singature(self):
        signer1 = self.create_signer({
            'email': self.test_email,
        })
        self.assertRaises(BadSignature, signer1.verify)


class ExampleSignerTestCase(BaseTestSignerMixin, TestCase):
    cls = ExampleSigner


class ExampleTimestampSignerTestCase(BaseTestSignerMixin, TestCase):
    cls = ExampleTimestampSigner

    def test_signer_timestamp_present(self):
        signer = self.create_signer({
            'email': self.test_email,
        })
        signed_data = signer.get_signed_data()
        self.assertSetEqual(
            set(signed_data.keys()),
            {'email', 'timestamp', 'signature'},
        )

    def test_verify_missing_timestamp(self):
        timestamp = int(time.time())
        with patch('time.time',
                   side_effect=lambda: timestamp):
            signer1 = self.create_signer({
                'email': self.test_email,
            })
        signed_data = signer1.get_signed_data()
        del signed_data['timestamp']
        with patch('time.time',
                   side_effect=lambda: timestamp + 1):
            signer2 = self.create_signer(signed_data)
            self.assertRaises(BadSignature, signer2.verify)

    def test_verify_expired(self):
        timestamp = int(time.time())
        with patch('time.time',
                   side_effect=lambda: timestamp):
            signer1 = self.create_signer({
                'email': self.test_email,
            })
            signed_data = signer1.get_signed_data()

        signer2 = self.create_signer(signed_data)
        with patch('time.time',
                   side_effect=lambda: timestamp + 3600 * 24 * 2):
            self.assertRaises(SignatureExpired, signer2.verify)


class ExampleURLSignerTestCase(BaseTestSignerMixin, TestCase):
    cls = ExampleURLSigner

    def setUp(self):
        self.factory = APIRequestFactory()
        self.request = self.factory.get('')

    def create_signer(self, data):
        return self.cls(data, self.request)

    def test_get_url(self):
        signer = self.create_signer({
            'email': self.test_email,
        })
        url = signer.get_url()
        self.assertIn(self.cls.BASE_URL, url)
        self.assertIn(urlencode({'email': self.test_email}), url)

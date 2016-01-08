import datetime

from django.core.signing import BadSignature
from django.test import TestCase

from rest_registration.verification import DataSigner, URLParamsSigner


class TestSigner(DataSigner):
    pass


class TimestampTestSigner(DataSigner):
    use_timestamp = True
    valid_period = datetime.timedelta(days=1)


class URLTestSigner(URLParamsSigner):
    base_url = '/test_url/'
    use_timestamp = True
    valid_period = datetime.timedelta(days=1)


class BaseTestSignerMixin(object):
    cls = None

    def create_signer(self, data):
        return self.cls(data)

    def test_sign_ok(self):
        test_email = 'test@example.com'
        signer1 = self.create_signer({
            'email': test_email,
        })
        signed_data = signer1.get_signed_data()
        signer2 = self.create_signer(signed_data)
        signer2.verify()
        signer2.verify()

    def test_sign_fail(self):
        test_email = 'test@example.com'
        signer1 = self.create_signer({
            'email': test_email,
        })
        self.assertRaises(BadSignature, signer1.verify)


class TestSignerTestCase(BaseTestSignerMixin, TestCase):
    cls = TestSigner


class TimestampTestSignerTestCase(BaseTestSignerMixin, TestCase):
    cls = TimestampTestSigner

    def test_sign_timestam_ok(self):
        test_email = 'test@example.com'
        signer = self.create_signer({
            'email': test_email,
        })
        signed_data = signer.get_signed_data()
        self.assertSetEqual(
            set(signed_data.keys()),
            {'email', 'timestamp', 'signature'},
        )


class URLTestSignerTestCase(BaseTestSignerMixin, TestCase):
    cls = URLTestSigner

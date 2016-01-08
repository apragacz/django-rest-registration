import pickle
import time
from urllib.parse import urlencode

from django.core.signing import BadSignature, SignatureExpired, base64_hmac
from django.conf import settings
from django.utils.crypto import constant_time_compare


def hash_simple_dict(salt, data, key=None):
    data_items = sorted([(str(k), str(v)) for k, v in data.items()])
    value = pickle.dumps(data_items, pickle.HIGHEST_PROTOCOL)
    return base64_hmac(salt, value, key=key)


def get_current_timestamp():
    return int(time.time())


class DataSigner(object):
    signature_field = 'signature'
    timestamp_field = 'timestamp'
    salt = 'rest-registration-default-salt'
    use_timestamp = False
    vaid_period = None

    def __init__(self, data):
        if self.use_timestamp and self.timestamp_field not in data:
            data = data.copy()
            data[self.timestamp_field] = get_current_timestamp()
        self._data = data

    def _calculate_signature(self, data):
        if self.signature_field in data:
            data = data.copy()
            del data[self.signature_field]
        return hash_simple_dict(self.salt, data)

    def calculate_signature(self):
        return self._calculate_signature(self._data)

    def get_signed_data(self):
        data = self._data.copy()
        data[self.signature_field] = self.calculate_signature()
        return data

    def verify(self):
        data = self._data
        signature = data.get(self.signature_field, None)
        if signature is None:
            raise BadSignature()
        expected_signature = self.calculate_signature()
        if not constant_time_compare(signature, expected_signature):
            raise BadSignature()

        if self.use_timestamp and self.vaid_period is not None:
            timestamp = data.get(self.timestamp_field, None)
            if timestamp is None:
                raise BadSignature()

            timestamp = int(timestamp)
            current_timestamp = get_current_timestamp()
            valid_period_secs = self.vaid_period.total_seconds()
            if current_timestamp - timestamp > valid_period_secs:
                raise SignatureExpired()


class URLParamsSigner(DataSigner):
    base_url = None

    def __init__(self, data, request=None):
        assert self.base_url, 'base_url is not defined'
        super().__init__(data)
        self.request = request

    def get_url(self):
        params = urlencode(self.get_signed_data())
        url = self.base_url + "?" + params
        if self.request:
            url = self.request.build_absolute_uri(url)
        return url

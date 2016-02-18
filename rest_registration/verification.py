import pickle
import time
from urllib.parse import urlencode

from django.core.signing import BadSignature, SignatureExpired, Signer
from django.utils.crypto import constant_time_compare


def get_current_timestamp():
    return int(time.time())


def get_dict_repr(data):
    data_items = sorted([(str(k), str(v)) for k, v in data.items()])
    return pickle.dumps(data_items, pickle.HIGHEST_PROTOCOL)


class DataSigner(object):
    signature_field = 'signature'
    timestamp_field = 'timestamp'
    salt = 'rest-registration-default-salt'
    use_timestamp = False
    valid_period = None

    def __init__(self, data):
        if self.use_timestamp and self.timestamp_field not in data:
            data = data.copy()
            data[self.timestamp_field] = get_current_timestamp()
        self._data = data
        self._signer = Signer(self.salt)

    def hash_simple_dict(salt, data, key=None):
        data_items = sorted([(str(k), str(v)) for k, v in data.items()])
        value = pickle.dumps(data_items, pickle.HIGHEST_PROTOCOL)
        return base64_hmac(salt, value, key=key)

    def _calculate_signature(self, data):
        if self.signature_field in data:
            data = data.copy()
            del data[self.signature_field]
        return self._signer.signature(get_dict_repr(data))

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

        if self.use_timestamp and self.valid_period is not None:
            timestamp = data[self.timestamp_field]
            timestamp = int(timestamp)
            current_timestamp = get_current_timestamp()
            valid_period_secs = self.valid_period.total_seconds()
            if current_timestamp - timestamp > valid_period_secs:
                raise SignatureExpired()


class URLParamsSigner(DataSigner):
    base_url = None

    def __init__(self, data, request=None, strict=True):
        assert not strict or self.base_url, 'base_url is not defined'
        super().__init__(data)
        self.request = request

    def get_url(self):
        params = urlencode(self.get_signed_data())
        url = self.base_url + "?" + params
        if self.request:
            url = self.request.build_absolute_uri(url)
        return url

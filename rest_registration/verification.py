import pickle
import time
from urllib.parse import urlencode

from django.core.signing import BadSignature, SignatureExpired, Signer
from django.utils.crypto import constant_time_compare

PICKLE_REPR_PROTOCOL = 4


def get_current_timestamp():
    return int(time.time())


def get_dict_repr(data):
    data_items = sorted([(str(k), str(v)) for k, v in data.items()])
    return pickle.dumps(data_items, PICKLE_REPR_PROTOCOL)


class DataSigner(object):
    SIGNATURE_FIELD = 'signature'
    TIMESTAMP_FIELD = 'timestamp'
    SALT_BASE = 'rest-registration-default-salt'
    USE_TIMESTAMP = False
    VALID_PERIOD = None

    def __init__(self, data):
        if self.USE_TIMESTAMP and self.TIMESTAMP_FIELD not in data:
            data = data.copy()
            data[self.TIMESTAMP_FIELD] = get_current_timestamp()
        self._data = data
        self._salt = self._calculate_salt(data)
        self._signer = Signer(self._salt)

    def _calculate_signature(self, data):
        if self.SIGNATURE_FIELD in data:
            data = data.copy()
            del data[self.SIGNATURE_FIELD]
        return self._signer.signature(get_dict_repr(data))

    def calculate_signature(self):
        return self._calculate_signature(self._data)

    def get_signed_data(self):
        data = self._data.copy()
        data[self.SIGNATURE_FIELD] = self.calculate_signature()
        return data

    def get_valid_period(self):
        return self.VALID_PERIOD

    def _calculate_salt(self, data):
        return self.SALT_BASE

    def verify(self):
        data = self._data
        signature = data.get(self.SIGNATURE_FIELD, None)
        if signature is None:
            raise BadSignature()
        expected_signature = self.calculate_signature()
        if not constant_time_compare(signature, expected_signature):
            raise BadSignature()

        valid_period = self.get_valid_period()

        if self.USE_TIMESTAMP and valid_period is not None:
            timestamp = data[self.TIMESTAMP_FIELD]
            timestamp = int(timestamp)
            current_timestamp = get_current_timestamp()
            valid_period_secs = valid_period.total_seconds()
            if current_timestamp - timestamp > valid_period_secs:
                raise SignatureExpired()


class URLParamsSigner(DataSigner):
    BASE_URL = None

    def get_base_url(self):
        return self.BASE_URL

    def __init__(self, data, request=None, strict=True):
        base_url = self.get_base_url()
        assert not strict or base_url, 'base_url is not defined'
        super().__init__(data)
        self.request = request

    def get_url(self):
        base_url = self.get_base_url()
        params = urlencode(self.get_signed_data())
        url = '{base_url}?{params}'.format(base_url=base_url, params=params)
        if self.request:
            url = self.request.build_absolute_uri(url)
        return url

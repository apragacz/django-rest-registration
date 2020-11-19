from urllib.parse import urlencode

from django.core import signing
from rest_framework.settings import api_settings

from rest_registration.exceptions import SignatureExpired, SignatureInvalid
from rest_registration.settings import registration_settings


def verify_signer_or_bad_request(signer):
    try:
        signer.verify()
    except signing.SignatureExpired:
        if registration_settings.USE_NON_FIELD_ERRORS_KEY_FROM_DRF_SETTINGS:
            raise SignatureExpired({
                api_settings.NON_FIELD_ERRORS_KEY: [SignatureExpired.default_detail]
            }) from None
        raise SignatureExpired() from None
    except signing.BadSignature:
        if registration_settings.USE_NON_FIELD_ERRORS_KEY_FROM_DRF_SETTINGS:
            raise SignatureInvalid({
                api_settings.NON_FIELD_ERRORS_KEY: [SignatureInvalid.default_detail]
            }) from None
        raise SignatureInvalid() from None


def build_default_verification_url(signer):
    base_url = signer.get_base_url()
    params = urlencode(signer.get_signed_data())
    url = '{base_url}?{params}'.format(base_url=base_url, params=params)
    if signer.request:
        url = signer.request.build_absolute_uri(url)
    return url


def build_default_template_context(
        user, user_address, data,
        notification_type=None, notification_method=None):
    context = {
        'user': user,
        'email': user_address,
    }
    data = data.copy()
    params_signer = data.pop('params_signer', None)
    if params_signer:
        context['verification_url'] = params_signer.get_url()
    context.update(data)
    return context

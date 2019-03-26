from urllib.parse import urlencode

from django.core.signing import BadSignature, SignatureExpired

from rest_registration.exceptions import BadRequest


def verify_signer_or_bad_request(signer):
    try:
        signer.verify()
    except SignatureExpired:
        raise BadRequest('Signature expired')
    except BadSignature:
        raise BadRequest('Invalid signature')


def build_default_verification_url(signer):
    base_url = signer.get_base_url()
    params = urlencode(signer.get_signed_data())
    url = '{base_url}?{params}'.format(base_url=base_url, params=params)
    if signer.request:
        url = signer.request.build_absolute_uri(url)
    return url

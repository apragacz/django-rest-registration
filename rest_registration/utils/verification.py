from django.core.signing import BadSignature, SignatureExpired

from rest_registration.exceptions import BadRequest


def verify_signer_or_bad_request(signer):
    try:
        signer.verify()
    except SignatureExpired:
        raise BadRequest('Signature expired')
    except BadSignature:
        raise BadRequest('Invalid signature')

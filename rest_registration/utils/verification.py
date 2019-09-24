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


def build_default_template_context(
        user, user_address, data,
        notification_type=None, notification_method=None):
    context = {
        'user': user,
        'email': user_address,
    }
    params_signer = data.get('params_signer')
    if params_signer:
        context['verification_url'] = params_signer.get_url()
    return context

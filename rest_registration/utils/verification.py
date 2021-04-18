from typing import TYPE_CHECKING, Any, Dict, Optional
from urllib.parse import urlencode

from django.core import signing

from rest_registration.exceptions import SignatureExpired, SignatureInvalid
from rest_registration.notifications.enums import NotificationMethod, NotificationType
from rest_registration.utils.signers import URLParamsSigner

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser


def verify_signer_or_bad_request(signer: URLParamsSigner) -> None:
    try:
        signer.verify()
    except signing.SignatureExpired:
        raise SignatureExpired() from None
    except signing.BadSignature:
        raise SignatureInvalid() from None


def build_default_verification_url(signer: URLParamsSigner) -> str:
    base_url = signer.get_base_url()
    params = urlencode(signer.get_signed_data())
    url = '{base_url}?{params}'.format(base_url=base_url, params=params)
    if signer.request:
        url = signer.request.build_absolute_uri(url)
    return url


def build_default_template_context(
        user: 'AbstractBaseUser',
        user_address: Any,
        data: Dict[str, Any],
        notification_type: Optional[NotificationType] = None,
        notification_method: Optional[NotificationMethod] = None) -> Dict[str, Any]:
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

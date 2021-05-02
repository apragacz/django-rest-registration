from typing import TYPE_CHECKING, Any, Dict, Optional
from urllib.parse import urlencode

from django.core import signing
from rest_framework.request import Request

from rest_registration.exceptions import SignatureExpired, SignatureInvalid
from rest_registration.notifications.enums import NotificationMethod, NotificationType
from rest_registration.settings import registration_settings
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


def select_default_templates(
        request: Request,
        user: 'AbstractBaseUser',
        notification_type: NotificationType,
        notification_method: NotificationMethod) -> Dict[str, str]:
    mapping = _get_default_email_templates_mapping()
    assert notification_type in mapping
    # Note: in case of KeyError we should raise VerificationTemplatesNotFound,
    # but that's not expected as we're covering all the cases here.
    return mapping[notification_type]


def _get_default_email_templates_mapping() -> Dict[NotificationType, Dict[str, str]]:
    return {
        NotificationType.REGISTER_VERIFICATION: registration_settings.REGISTER_VERIFICATION_EMAIL_TEMPLATES,  # noqa: E501
        NotificationType.REGISTER_EMAIL_VERIFICATION: registration_settings.REGISTER_EMAIL_VERIFICATION_EMAIL_TEMPLATES,  # noqa: E501
        NotificationType.RESET_PASSWORD_VERIFICATION: registration_settings.RESET_PASSWORD_VERIFICATION_EMAIL_TEMPLATES,  # noqa: E501
    }

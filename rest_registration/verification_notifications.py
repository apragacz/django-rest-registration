from typing import TYPE_CHECKING, Dict

from rest_framework.request import Request

from rest_registration.exceptions import VerificationTemplatesNotFound
from rest_registration.notifications.email import send_verification_notification
from rest_registration.notifications.enums import NotificationMethod, NotificationType
from rest_registration.settings import registration_settings
from rest_registration.signers.register import RegisterSigner
from rest_registration.signers.register_email import RegisterEmailSigner
from rest_registration.signers.reset_password import ResetPasswordSigner
from rest_registration.utils.users import get_user_verification_id
from rest_registration.utils.verification import select_default_templates

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser


def send_register_verification_email_notification(
        request: Request,
        user: 'AbstractBaseUser',
) -> None:
    signer = RegisterSigner({
        'user_id': get_user_verification_id(user),
    }, request=request)
    template_config_data = _get_email_template_config_data(
        request, user, NotificationType.REGISTER_VERIFICATION)
    notification_data = {
        'params_signer': signer,
    }
    send_verification_notification(
        NotificationType.REGISTER_VERIFICATION, user,
        notification_data, template_config_data)


def send_register_email_verification_email_notification(
        request: Request,
        user: 'AbstractBaseUser',
        email: str,
        email_already_used: bool = False,
) -> None:
    signer = RegisterEmailSigner({
        'user_id': get_user_verification_id(user),
        'email': email,
    }, request=request)
    notification_data = {
        'params_signer': signer,
        'email_already_used': email_already_used,
    }
    template_config_data = _get_email_template_config_data(
        request, user, NotificationType.REGISTER_EMAIL_VERIFICATION)
    send_verification_notification(
        NotificationType.REGISTER_EMAIL_VERIFICATION, user,
        notification_data, template_config_data, custom_user_address=email)


def send_reset_password_verification_email_notification(
        request: Request,
        user: 'AbstractBaseUser',
) -> None:
    signer = ResetPasswordSigner({
        'user_id': get_user_verification_id(user),
    }, request=request)

    template_config_data = _get_email_template_config_data(
        request, user, NotificationType.RESET_PASSWORD_VERIFICATION)
    notification_data = {
        'params_signer': signer,
    }
    send_verification_notification(
        NotificationType.RESET_PASSWORD_VERIFICATION, user, notification_data,
        template_config_data)


def _get_email_template_config_data(
        request: Request,
        user: 'AbstractBaseUser',
        notification_type: NotificationType,
) -> Dict[str, str]:
    template_selector = registration_settings.VERIFICATION_TEMPLATES_SELECTOR
    notification_method = NotificationMethod.EMAIL
    try:
        template_config_data = template_selector(
            request=request,
            user=user,
            notification_method=notification_method,
            notification_type=notification_type,
        )
    except (VerificationTemplatesNotFound, LookupError):
        template_config_data = select_default_templates(
            request=request,
            user=user,
            notification_method=notification_method,
            notification_type=notification_type,
        )
    return template_config_data

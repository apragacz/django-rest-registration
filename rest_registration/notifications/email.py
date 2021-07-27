from typing import TYPE_CHECKING, Any, Dict

from django.core.mail.message import EmailMultiAlternatives

from rest_registration.notifications.enums import NotificationMethod, NotificationType
from rest_registration.settings import registration_settings
from rest_registration.utils.users import get_user_email_field_name

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser


def send_verification_notification(
        notification_type: NotificationType,
        user: 'AbstractBaseUser',
        data: Dict[str, Any],
        template_config_data: Dict[str, Any],
        custom_user_address: Any = None) -> None:
    if custom_user_address is None:
        user_address = get_user_address(user)
    else:
        user_address = custom_user_address
    notification = create_verification_notification(
        notification_type, user, user_address, data, template_config_data)
    send_notification(notification)


def create_verification_notification(
        notification_type: NotificationType,
        user: 'AbstractBaseUser',
        user_address: Any,
        data: Dict[str, Any],
        template_config_data: Dict[str, Any]) -> EmailMultiAlternatives:
    from_email = registration_settings.VERIFICATION_FROM_EMAIL
    reply_to_email = (registration_settings.VERIFICATION_REPLY_TO_EMAIL or
                      from_email)
    template_context_builder = registration_settings.VERIFICATION_TEMPLATE_CONTEXT_BUILDER  # noqa: E501
    context = template_context_builder(
        user, user_address, data,
        notification_type=notification_type,
        notification_method=NotificationMethod.EMAIL)

    template_builder = registration_settings.VERIFICATION_TEMPLATE_RENDERER  # noqa: E501
    template_data = template_builder(template_config_data, context)

    email_msg = EmailMultiAlternatives(
        subject=template_data.subject,
        body=template_data.text_body,
        from_email=from_email,
        to=[user_address],
        reply_to=[reply_to_email]
    )
    if template_data.html_body:
        email_msg.attach_alternative(template_data.html_body, 'text/html')

    return email_msg


def send_notification(notification: EmailMultiAlternatives) -> None:
    notification.send()


def get_user_address(user: 'AbstractBaseUser') -> str:
    email_field_name = get_user_email_field_name()
    email = getattr(user, email_field_name)  # type: str
    return email

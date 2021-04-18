from typing import TYPE_CHECKING, Dict

from rest_framework.request import Request

from rest_registration.exceptions import VerificationTemplatesNotFound
from rest_registration.notifications.enums import NotificationMethod, NotificationType

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser


def select_verification_templates(
        request: Request,
        user: 'AbstractBaseUser',
        notification_type: NotificationType,
        notification_method: NotificationMethod) -> Dict[str, str]:
    return {
        'subject': 'rest_registration_custom/generic/subject.txt',
        'body': 'rest_registration_custom/generic/body.txt',
    }


def faulty_select_verification_templates(
        request: Request,
        user: 'AbstractBaseUser',
        notification_type: NotificationType,
        notification_method: NotificationMethod) -> Dict[str, str]:
    raise VerificationTemplatesNotFound()

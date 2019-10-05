from enum import Enum


class NotificationType(Enum):
    REGISTER_VERIFICATION = 1
    REGISTER_EMAIL_VERIFICATION = 2
    RESET_PASSWORD_VERIFICATION = 3


class NotificationMethod(Enum):
    EMAIL = 1

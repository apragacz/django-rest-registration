from enum import Enum, auto


class NotificationType(Enum):
    REGISTER_VERIFICATION = auto()
    REGISTER_EMAIL_VERIFICATION = auto()
    RESET_PASSWORD_VERIFICATION = auto()


class NotificationMethod(Enum):
    EMAIL = auto()

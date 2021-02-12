from enum import Enum


class ErrorCode(Enum):
    NO_RESET_PASSWORD_VER_URL = 1
    NO_REGISTER_VER_URL = 2
    NO_REGISTER_EMAIL_VER_URL = 3
    NO_VER_FROM_EMAIL = 4
    NO_TOKEN_AUTH_CONFIG = 5
    NO_TOKEN_AUTH_INSTALLED = 6
    INVALID_EMAIL_TEMPLATE_CONFIG = 7
    NO_AUTH_INSTALLED = 8
    DRF_INCOMPATIBLE_DJANGO_AUTH_BACKEND = 9
    LOGIN_FIELDS_NOT_UNIQUE = 10
    INVALID_AUTH_TOKEN_MANAGER_CLASS = 11
    INVALID_REGISTER_EMAIL_SERIALIZER_CLASS = 12
    NON_UNIQUE_FIELD_USED_AS_UNIQUE = 13

    def __str__(self):
        return 'E{self.value:03d}'.format(self=self)


class WarningCode(Enum):
    REGISTER_VERIFICATION_MULTIPLE_AUTO_LOGIN = 1
    DEPRECATION = 2

    def __str__(self):
        return 'W{self.value:03d}'.format(self=self)

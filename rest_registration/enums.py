from enum import Enum
from typing import Type

from django.core import checks

from rest_registration.utils.checks import CheckCode, CheckMessage


class _BaseCheckCodeMixin(CheckCode):  # noqa: E501 pylint: disable=abstract-method

    def get_app_name(self) -> str:
        from rest_registration.apps import RestRegistrationConfig  # noqa: E501 pylint: disable=import-outside-toplevel, cyclic-import
        return RestRegistrationConfig.name


class ErrorCode(_BaseCheckCodeMixin, Enum):
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
    INVALID_AUTH_BACKENDS_CONFIG = 14

    def get_code_id(self) -> str:
        return 'E{self.value:03d}'.format(self=self)

    def get_check_message_class(self) -> Type[CheckMessage]:
        return checks.Error

    def __str__(self) -> str:
        return self.get_code_id()


class WarningCode(_BaseCheckCodeMixin, Enum):
    REGISTER_VERIFICATION_MULTIPLE_AUTO_LOGIN = 1
    DEPRECATION = 2

    def get_code_id(self) -> str:
        return 'W{self.value:03d}'.format(self=self)

    def get_check_message_class(self) -> Type[CheckMessage]:
        return checks.Warning

    def __str__(self) -> str:
        return self.get_code_id()

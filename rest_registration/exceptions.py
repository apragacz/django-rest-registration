from typing import Dict, List, Optional, Union

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException as _APIException
from rest_framework.settings import api_settings

from rest_registration.settings import registration_settings

DetailType = Union[str, List[str], Dict[str, List[str]]]


class APIException(_APIException):

    def __init__(
            self,
            detail: Optional[DetailType] = None,
            code: Optional[str] = None) -> None:
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code

        if registration_settings.USE_NON_FIELD_ERRORS_KEY_FROM_DRF_SETTINGS:
            detail = _wrap_detail_in_dict(detail)

        super().__init__(detail=detail, code=code)


class BadRequest(APIException):
    status_code = 400
    default_detail = _("Bad Request")
    default_code = 'bad-request'


class UserNotFound(BadRequest):
    default_detail = _("User not found")
    default_code = 'user-not-found'


class LoginInvalid(BadRequest):
    default_detail = _("Login or password invalid.")
    default_code = 'login-invalid'


class EmailAlreadyRegistered(BadRequest):
    default_detail = _("This email is already registered.")
    default_code = 'email-already-registered'


class UserWithoutEmailNonverifiable(BadRequest):
    default_detail = _("User without email cannot be verified")
    default_code = 'user-without-email-nonverifiable'


class AuthTokenError(BadRequest):
    default_detail = _("Could not process authentication token")
    default_code = 'auth-token-error'


class AuthTokenNotProvided(AuthTokenError):
    default_detail = _("Authentication token could not be provided")
    default_code = 'auth-token-not-provided'


class AuthTokenNotRevoked(AuthTokenError):
    default_detail = _("Authentication token cannot be revoked")
    default_code = 'auth-token-not-revoked'


class AuthTokenNotFound(AuthTokenError):
    default_detail = _("Authentication token not found")
    default_code = 'auth-token-not-found'


class SignatureError(BadRequest):
    default_detail = _("Generic signature error")
    default_code = 'signature-error'


class SignatureExpired(SignatureError):
    default_detail = _("Signature expired")
    default_code = 'signature-expired'


class SignatureInvalid(SignatureError):
    default_detail = _("Invalid signature")
    default_code = 'signature-invalid'


class VerificationTemplatesNotFound(APIException):
    status_code = 500
    default_detail = _("Could not find verification templates")
    default_code = 'verification-templates-not-found'


def _wrap_detail_in_dict(detail: DetailType) -> Dict[str, List[str]]:
    if isinstance(detail, list):
        return {api_settings.NON_FIELD_ERRORS_KEY: detail}
    if isinstance(detail, dict):
        return detail
    return {api_settings.NON_FIELD_ERRORS_KEY: [detail]}

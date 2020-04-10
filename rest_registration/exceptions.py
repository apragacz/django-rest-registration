from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import APIException


class BadRequest(APIException):
    status_code = 400
    default_detail = _("Bad Request")
    default_code = 'bad-request'


class UserNotFound(APIException):
    status_code = 404
    default_detail = _("User not found")
    default_code = 'user-not-found'


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

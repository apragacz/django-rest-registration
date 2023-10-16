from typing import TYPE_CHECKING, Optional, Sequence, Type

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

from rest_registration.auth_token_managers import AbstractAuthTokenManager, AuthToken
from rest_registration.exceptions import AuthTokenNotProvided, AuthTokenNotRevoked

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser


class FaultyAuthTokenManager(AbstractAuthTokenManager):

    def get_authentication_class(self):
        return BaseAuthentication

    def provide_token(self, user):
        raise AuthTokenNotProvided()


class AuthJWTManager(AbstractAuthTokenManager):

    def get_authentication_class(self) -> Type[BaseAuthentication]:
        return JWTAuthentication

    def get_app_names(self) -> Sequence[str]:
        return [
            'tests.testapps.custom_authtokens',  # update with your Django app
        ]

    def provide_token(self, user: 'AbstractBaseUser') -> AuthToken:
        encoded_jwt = jwt.encode(
            {"user_id": user.pk},
            settings.SECRET_KEY,
            algorithm=JWTAuthentication.ALGORITHM,
        )
        return AuthToken(encoded_jwt)

    def revoke_token(
            self, user: 'AbstractBaseUser', *,
            token: Optional[AuthToken] = None) -> None:
        raise AuthTokenNotRevoked()


class JWTAuthentication(BaseAuthentication):
    ALGORITHM = "HS256"

    def authenticate(self, request):
        """
        Returns a `User` if a correct username and password have been supplied
        using HTTP Basic authentication.  Otherwise returns `None`.
        """
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'bearer':
            return None

        if len(auth) == 1:
            msg = _('Invalid authorization header. No credentials provided.')
            raise AuthenticationFailed(msg)
        if len(auth) > 2:
            msg = _(
                'Invalid authorization header. Credentials string should not'
                ' contain spaces.'
            )
            raise AuthenticationFailed(msg)

        encoded_jwt = auth[1]

        try:
            jwt_data = jwt.decode(
                encoded_jwt,
                settings.SECRET_KEY,
                algorithms=[self.ALGORITHM],
            )
        except jwt.ExpiredSignatureError:
            msg = _('Expired JWT.')
            raise AuthenticationFailed(msg) from None
        except jwt.InvalidTokenError:
            msg = _('Invalid JWT payload.')
            raise AuthenticationFailed(msg) from None

        try:
            user_id = jwt_data["user_id"]
        except KeyError:
            msg = _('Missing user info in JWT.')
            raise AuthenticationFailed(msg) from None

        user_class = get_user_model()
        try:
            user = user_class.objects.get(pk=user_id)
        except user_class.DoesNotExist:
            msg = _('User not found.')
            raise AuthenticationFailed(msg) from None

        return (user, encoded_jwt)

from typing import TYPE_CHECKING, NewType, Optional, Sequence, Type

from rest_framework.authentication import BaseAuthentication, TokenAuthentication

from rest_registration.exceptions import AuthTokenNotFound, AuthTokenNotRevoked

AuthToken = NewType('AuthToken', str)

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser


class AbstractAuthTokenManager:

    def get_authentication_class(self) -> Type[BaseAuthentication]:
        """
        Return authentication class which is able to parse the token.
        This is used to ensure that the class is added
        in ``REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES']`` setting.
        """
        raise NotImplementedError()

    def get_app_names(self) -> Sequence[str]:
        """
        Return the Django app names which need to be installed so
        this token manager class works properly.

        Overriding this method is not required but recommended as it provides
        additional check during the Django startup.
        """
        return []

    def provide_token(self, user: 'AbstractBaseUser') -> AuthToken:
        """
        Get or create token for given user.
        If there is no token to provide,
        raise ``rest_registration.exceptions.AuthTokenError``.
        """
        raise NotImplementedError()

    def revoke_token(
            self, user: 'AbstractBaseUser', *,
            token: Optional[AuthToken] = None) -> None:
        """
        Revoke the given token for a given user. If the token is not provided,
        revoke all tokens for given user.
        If the provided token is invalid or there is no token to revoke,
        raise ``rest_registration.exceptions.AuthTokenError``.

        This method may not be implemented in all cases - for instance, in case
        when the token is cryptographically generated and not stored
        in the database.
        """
        raise AuthTokenNotRevoked()


class RestFrameworkAuthTokenManager(AbstractAuthTokenManager):

    def get_authentication_class(self) -> Type[BaseAuthentication]:
        return TokenAuthentication

    def get_app_names(self) -> Sequence[str]:
        return [
            'rest_framework.authtoken',
        ]

    def provide_token(self, user: 'AbstractBaseUser') -> AuthToken:
        from rest_framework.authtoken.models import Token  # noqa: E501 pylint: disable=import-outside-toplevel

        token_obj, _ = Token.objects.get_or_create(user=user)
        return AuthToken(token_obj.key)

    def revoke_token(
            self, user: 'AbstractBaseUser', *,
            token: Optional[AuthToken] = None) -> None:
        from rest_framework.authtoken.models import Token  # noqa: E501 pylint: disable=import-outside-toplevel

        try:
            token_obj = Token.objects.get(user_id=user.pk)  # type: Token
        except Token.DoesNotExist:
            raise AuthTokenNotFound() from None

        if token is not None and token_obj.key != token:
            raise AuthTokenNotFound() from None

        token_obj.delete()

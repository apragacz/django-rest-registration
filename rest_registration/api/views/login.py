from typing import TYPE_CHECKING, Any, Dict, Type

from django.contrib import auth
from django.utils.translation import gettext as _
from rest_framework import permissions, serializers
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.settings import api_settings

from rest_registration.api.views.base import BaseAPIView
from rest_registration.exceptions import LoginInvalid, UserNotFound
from rest_registration.settings import registration_settings
from rest_registration.utils.auth_backends import get_login_authentication_backend
from rest_registration.utils.responses import get_ok_response

if TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser

    from rest_registration.auth_token_managers import AbstractAuthTokenManager


class LoginView(BaseAPIView):
    permission_classes = registration_settings.NOT_AUTHENTICATED_PERMISSION_CLASSES

    def post(self, request: Request) -> Response:
        '''
        Logs in the user via given login and password.
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        login_authenticator = registration_settings.LOGIN_AUTHENTICATOR
        try:
            user = login_authenticator(serializer.validated_data, serializer=serializer)
        except UserNotFound:
            raise LoginInvalid() from None

        extra_data = perform_login(request, user)

        return get_ok_response(_("Login successful"), extra_data=extra_data)

    def get_serializer_class(self) -> Type[Serializer]:
        return registration_settings.LOGIN_SERIALIZER_CLASS


login = LoginView.as_view()


class LogoutSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    revoke_token = serializers.BooleanField(default=False)


class LogoutView(BaseAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        '''
        Logs out the user. returns an error if the user is not
        authenticated.
        '''
        user = request.user
        assert not user.is_anonymous
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if should_authenticate_session():
            auth.logout(request)
        if should_retrieve_token() and data['revoke_token']:
            auth_token_manager_cls = registration_settings.AUTH_TOKEN_MANAGER_CLASS
            auth_token_manager: AbstractAuthTokenManager = auth_token_manager_cls()  # noqa: E501
            auth_token_manager.revoke_token(user)

        return get_ok_response(_("Logout successful"))


logout = LogoutView.as_view()


def should_authenticate_session() -> bool:
    result = registration_settings.LOGIN_AUTHENTICATE_SESSION
    if result is None:
        result = rest_auth_has_class(SessionAuthentication)
    return result


def should_retrieve_token() -> bool:
    result = registration_settings.LOGIN_RETRIEVE_TOKEN
    if result is None:
        result = rest_auth_has_class(TokenAuthentication)
    return result


def rest_auth_has_class(cls: type) -> bool:
    return cls in api_settings.DEFAULT_AUTHENTICATION_CLASSES


def perform_login(request: Request, user: 'AbstractBaseUser') -> Dict[str, Any]:
    if should_authenticate_session():
        login_auth_backend = get_login_authentication_backend(user=user)
        auth.login(request, user, backend=login_auth_backend)

    extra_data = {}

    if should_retrieve_token():
        auth_token_manager_cls = registration_settings.AUTH_TOKEN_MANAGER_CLASS
        auth_token_manager = auth_token_manager_cls()  # noqa: E501 type: rest_registration.auth_token_managers.AbstractAuthTokenManager
        token = auth_token_manager.provide_token(user)
        extra_data['token'] = token

    return extra_data

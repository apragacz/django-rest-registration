from django.contrib import auth
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.authentication import (
    SessionAuthentication,
    TokenAuthentication
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings

from rest_registration.decorators import (
    api_view_serializer_class,
    api_view_serializer_class_getter
)
from rest_registration.exceptions import LoginInvalid, UserNotFound
from rest_registration.settings import registration_settings
from rest_registration.utils.responses import get_ok_response


@api_view_serializer_class_getter(
    lambda: registration_settings.LOGIN_SERIALIZER_CLASS)
@api_view(['POST'])
@permission_classes(registration_settings.NOT_AUTHENTICATED_PERMISSION_CLASSES)
def login(request):
    '''
    Logs in the user via given login and password.
    '''
    serializer_class = registration_settings.LOGIN_SERIALIZER_CLASS
    serializer = serializer_class(
        data=request.data,
        context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    login_authenticator = registration_settings.LOGIN_AUTHENTICATOR
    try:
        user = login_authenticator(
            serializer.validated_data, serializer=serializer)
    except UserNotFound:
        raise LoginInvalid() from None

    extra_data = perform_login(request, user)

    return get_ok_response(_("Login successful"), extra_data=extra_data)


class LogoutSerializer(serializers.Serializer):  # noqa: E501 pylint: disable=abstract-method
    revoke_token = serializers.BooleanField(default=False)


@api_view_serializer_class(LogoutSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    '''
    Logs out the user. returns an error if the user is not
    authenticated.
    '''
    user = request.user
    serializer = LogoutSerializer(
        data=request.data,
        context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    if should_authenticate_session():
        auth.logout(request)
    if should_retrieve_token() and data['revoke_token']:
        auth_token_manager_cls = registration_settings.AUTH_TOKEN_MANAGER_CLASS
        auth_token_manager = auth_token_manager_cls()  # noqa: E501 type: rest_registration.auth_token_managers.AbstractAuthTokenManager
        auth_token_manager.revoke_token(user)

    return get_ok_response(_("Logout successful"))


def should_authenticate_session():
    result = registration_settings.LOGIN_AUTHENTICATE_SESSION
    if result is None:
        result = rest_auth_has_class(SessionAuthentication)
    return result


def should_retrieve_token():
    result = registration_settings.LOGIN_RETRIEVE_TOKEN
    if result is None:
        result = rest_auth_has_class(TokenAuthentication)
    return result


def rest_auth_has_class(cls):
    return cls in api_settings.DEFAULT_AUTHENTICATION_CLASSES


def perform_login(request, user):
    if should_authenticate_session():
        auth.login(request, user)

    extra_data = {}

    if should_retrieve_token():
        auth_token_manager_cls = registration_settings.AUTH_TOKEN_MANAGER_CLASS
        auth_token_manager = auth_token_manager_cls()  # noqa: E501 type: rest_registration.auth_token_managers.AbstractAuthTokenManager
        token = auth_token_manager.provide_token(user)
        extra_data['token'] = token

    return extra_data

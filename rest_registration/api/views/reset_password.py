from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import Http404
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from rest_registration.decorators import (
    api_view_serializer_class,
    api_view_serializer_class_getter
)
from rest_registration.exceptions import UserNotFound
from rest_registration.notifications.email import (
    send_verification_notification
)
from rest_registration.notifications.enums import NotificationType
from rest_registration.settings import registration_settings
from rest_registration.utils.responses import get_ok_response
from rest_registration.utils.users import (
    get_user_by_verification_id,
    get_user_verification_id
)
from rest_registration.utils.verification import verify_signer_or_bad_request
from rest_registration.verification import URLParamsSigner


class ResetPasswordSigner(URLParamsSigner):
    SALT_BASE = 'reset-password'
    USE_TIMESTAMP = True

    def get_base_url(self):
        return registration_settings.RESET_PASSWORD_VERIFICATION_URL

    def get_valid_period(self):
        return registration_settings.RESET_PASSWORD_VERIFICATION_PERIOD

    def _calculate_salt(self, data):
        if registration_settings.RESET_PASSWORD_VERIFICATION_ONE_TIME_USE:
            user = get_user_by_verification_id(
                data['user_id'], require_verified=False)
            user_password_hash = user.password
            # Use current user password hash as a part of the salt.
            # If the password gets changed, then assume that the change
            # was caused by previous password reset and the signature
            # is not valid anymore because changed password hash implies
            # changed salt used when verifying the input data.
            salt = '{self.SALT_BASE}:{user_password_hash}'.format(
                self=self, user_password_hash=user_password_hash)
        else:
            salt = self.SALT_BASE
        return salt


@api_view_serializer_class_getter(
    lambda: registration_settings.SEND_RESET_PASSWORD_LINK_SERIALIZER_CLASS)
@api_view(['POST'])
@permission_classes([AllowAny])
def send_reset_password_link(request):
    '''
    Send email with reset password link.
    '''
    if not registration_settings.RESET_PASSWORD_VERIFICATION_ENABLED:
        raise Http404()
    serializer_class = registration_settings.SEND_RESET_PASSWORD_LINK_SERIALIZER_CLASS  # noqa: E501
    serializer = serializer_class(
        data=request.data,
        context={'request': request},
    )
    serializer.is_valid(raise_exception=True)
    user = serializer.get_user_or_none()
    if not user:
        raise UserNotFound()
    signer = ResetPasswordSigner({
        'user_id': get_user_verification_id(user),
    }, request=request)

    template_config_data = registration_settings.RESET_PASSWORD_VERIFICATION_EMAIL_TEMPLATES  # noqa: E501
    notification_data = {
        'params_signer': signer,
    }
    send_verification_notification(
        NotificationType.RESET_PASSWORD_VERIFICATION, user, notification_data,
        template_config_data)

    return get_ok_response('Reset link sent')


class ResetPasswordSerializer(serializers.Serializer):  # noqa: E501 pylint: disable=abstract-method
    user_id = serializers.CharField(required=True)
    timestamp = serializers.IntegerField(required=True)
    signature = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


@api_view_serializer_class(ResetPasswordSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    '''
    Reset password, given the signature and timestamp from the link.
    '''
    process_reset_password_data(
        request.data, serializer_context={'request': request})
    return get_ok_response('Reset password successful')


def process_reset_password_data(input_data, serializer_context=None):
    if serializer_context is None:
        serializer_context = {}
    if not registration_settings.RESET_PASSWORD_VERIFICATION_ENABLED:
        raise Http404()
    serializer = ResetPasswordSerializer(
        data=input_data,
        context=serializer_context,
    )
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data.copy()
    password = data.pop('password')
    signer = ResetPasswordSigner(data)
    verify_signer_or_bad_request(signer)

    user = get_user_by_verification_id(data['user_id'], require_verified=False)
    try:
        validate_password(password, user=user)
    except ValidationError as exc:
        raise serializers.ValidationError(exc.messages[0])
    user.set_password(password)
    user.save()

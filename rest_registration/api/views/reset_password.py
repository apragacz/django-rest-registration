from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import Http404
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from rest_registration.decorators import api_view_serializer_class
from rest_registration.exceptions import UserNotFound
from rest_registration.notifications import send_verification_notification
from rest_registration.settings import registration_settings
from rest_registration.utils.responses import get_ok_response
from rest_registration.utils.users import (
    get_user_by_id,
    get_user_by_lookup_dict,
    get_user_setting
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
            user_id = data['user_id']
            user = get_user_by_id(user_id)
            # Use current user password hash as a part of the salt.
            # If the password gets changed, then assume that the change
            # was caused by previous password reset and the signature
            # is not valid anymore because changed password hash implies
            # changed salt used when verifying the input data.
            salt = '{self.SALT_BASE}:{user.password}'.format(
                self=self, user=user)
        else:
            salt = self.SALT_BASE
        return salt


class SendResetPasswordLinkSerializer(serializers.Serializer):
    login = serializers.CharField(required=True)


def get_login_fields():
    user_class = get_user_model()
    return get_user_setting('LOGIN_FIELDS') or [user_class.USERNAME_FIELD]


@api_view_serializer_class(SendResetPasswordLinkSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def send_reset_password_link(request):
    '''
    Send email with reset password link.
    '''
    if not registration_settings.RESET_PASSWORD_VERIFICATION_ENABLED:
        raise Http404()
    serializer = SendResetPasswordLinkSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    login = serializer.validated_data['login']

    user = None
    for login_field in get_login_fields():
        user = get_user_by_lookup_dict({login_field: login}, default=None)
        if user:
            break

    if not user:
        raise UserNotFound()

    signer = ResetPasswordSigner({
        'user_id': user.pk,
    }, request=request)

    template_config = (
        registration_settings.RESET_PASSWORD_VERIFICATION_EMAIL_TEMPLATES)
    send_verification_notification(user, signer, template_config)

    return get_ok_response('Reset link sent')


class ResetPasswordSerializer(serializers.Serializer):
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
    process_reset_password_data(request.data)
    return get_ok_response('Reset password successful')


def process_reset_password_data(input_data):
    if not registration_settings.RESET_PASSWORD_VERIFICATION_ENABLED:
        raise Http404()
    serializer = ResetPasswordSerializer(data=input_data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data.copy()
    password = data.pop('password')
    signer = ResetPasswordSigner(data)
    verify_signer_or_bad_request(signer)

    user = get_user_by_id(data['user_id'])
    try:
        validate_password(password, user=user)
    except ValidationError as exc:
        raise serializers.ValidationError(exc.messages[0])
    user.set_password(password)
    user.save()

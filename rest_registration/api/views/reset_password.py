from django.http import Http404
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes

from rest_registration.api.serializers import PasswordConfirmSerializerMixin
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
from rest_registration.utils.validation import (
    run_validators,
    validate_password_with_user_id,
    validate_user_password_confirm
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
@permission_classes(registration_settings.NOT_AUTHENTICATED_PERMISSION_CLASSES)
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
    if registration_settings.RESET_PASSWORD_FAIL_WHEN_USER_NOT_FOUND:
        success_message = _("Reset link sent")
    else:
        success_message = _("Reset link sent if the user exists in database")
    user = serializer.get_user_or_none()
    if not user:
        if registration_settings.RESET_PASSWORD_FAIL_WHEN_USER_NOT_FOUND:
            raise UserNotFound()
        return get_ok_response(success_message)
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

    return get_ok_response(success_message)


class ResetPasswordSerializer(  # pylint: disable=abstract-method
        PasswordConfirmSerializerMixin,
        serializers.Serializer):
    user_id = serializers.CharField(required=True)
    timestamp = serializers.IntegerField(required=True)
    signature = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def has_password_confirm_field(self):
        return registration_settings.RESET_PASSWORD_SERIALIZER_PASSWORD_CONFIRM

    def validate(self, attrs):
        validators = [
            validate_password_with_user_id,
        ]
        if self.has_password_confirm_field():
            validators.append(validate_user_password_confirm)
        run_validators(validators, attrs)
        return attrs


@api_view_serializer_class(ResetPasswordSerializer)
@api_view(['POST'])
@permission_classes(registration_settings.NOT_AUTHENTICATED_PERMISSION_CLASSES)
def reset_password(request):
    '''
    Reset password, given the signature and timestamp from the link.
    '''
    process_reset_password_data(
        request.data, serializer_context={'request': request})
    return get_ok_response(_("Reset password successful"))


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
    data.pop('password_confirm', None)
    signer = ResetPasswordSigner(data)
    verify_signer_or_bad_request(signer)

    user = get_user_by_verification_id(data['user_id'], require_verified=False)
    user.set_password(password)
    user.save()

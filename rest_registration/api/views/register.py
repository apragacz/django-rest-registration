from django.http import Http404
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from rest_registration import signals
from rest_registration.api.views.login import perform_login
from rest_registration.decorators import (
    api_view_serializer_class,
    api_view_serializer_class_getter
)
from rest_registration.exceptions import BadRequest
from rest_registration.notifications import send_verification_notification
from rest_registration.settings import registration_settings
from rest_registration.utils.responses import get_ok_response
from rest_registration.utils.users import (
    get_user_by_verification_id,
    get_user_setting,
    get_user_verification_id
)
from rest_registration.utils.verification import verify_signer_or_bad_request
from rest_registration.verification import URLParamsSigner


class RegisterSigner(URLParamsSigner):
    SALT_BASE = 'register'
    USE_TIMESTAMP = True

    def get_base_url(self):
        return registration_settings.REGISTER_VERIFICATION_URL

    def get_valid_period(self):
        return registration_settings.REGISTER_VERIFICATION_PERIOD

    def _calculate_salt(self, data):
        if registration_settings.REGISTER_VERIFICATION_ONE_TIME_USE:
            user = get_user_by_verification_id(
                data['user_id'], require_verified=False)
            # Use current user verification flag as a part of the salt.
            # If the verification flag gets changed, then assume that
            # the change was caused by previous verification and the signature
            # is not valid anymore because changed user verification flag
            # implies changed salt used when verifying the input data.
            verification_flag_field = get_user_setting(
                'VERIFICATION_FLAG_FIELD')
            verification_flag = getattr(user, verification_flag_field)
            salt = '{self.SALT_BASE}:{verification_flag}'.format(
                self=self, verification_flag=verification_flag)
        else:
            salt = self.SALT_BASE
        return salt


@api_view_serializer_class_getter(
    lambda: registration_settings.REGISTER_SERIALIZER_CLASS)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    '''
    Register new user.
    '''
    serializer_class = registration_settings.REGISTER_SERIALIZER_CLASS
    serializer = serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)

    kwargs = {}

    if registration_settings.REGISTER_VERIFICATION_ENABLED:
        verification_flag_field = get_user_setting('VERIFICATION_FLAG_FIELD')
        kwargs[verification_flag_field] = False
        email_field = get_user_setting('EMAIL_FIELD')
        if (email_field not in serializer.validated_data
                or not serializer.validated_data[email_field]):
            raise BadRequest("User without email cannot be verified")

    user = serializer.save(**kwargs)

    signals.user_registered.send(sender=None, user=user, request=request)
    output_serializer_class = registration_settings.REGISTER_OUTPUT_SERIALIZER_CLASS  # noqa: E501
    output_serializer = output_serializer_class(instance=user)
    user_data = output_serializer.data

    if registration_settings.REGISTER_VERIFICATION_ENABLED:
        signer = RegisterSigner({
            'user_id': get_user_verification_id(user),
        }, request=request)
        template_config = (
            registration_settings.REGISTER_VERIFICATION_EMAIL_TEMPLATES)
        send_verification_notification(user, signer, template_config)

    return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyRegistrationSerializer(serializers.Serializer):
    user_id = serializers.CharField(required=True)
    timestamp = serializers.IntegerField(required=True)
    signature = serializers.CharField(required=True)


@api_view_serializer_class(VerifyRegistrationSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_registration(request):
    """
    Verify registration via signature.
    """
    user = process_verify_registration_data(request.data)
    signals.user_activated.send(sender=None, user=user, request=request)
    extra_data = None
    if registration_settings.REGISTER_VERIFICATION_AUTO_LOGIN:
        extra_data = perform_login(request, user)
    return get_ok_response('User verified successfully', extra_data=extra_data)


def process_verify_registration_data(input_data):
    if not registration_settings.REGISTER_VERIFICATION_ENABLED:
        raise Http404()
    serializer = VerifyRegistrationSerializer(data=input_data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data
    signer = RegisterSigner(data)
    verify_signer_or_bad_request(signer)

    verification_flag_field = get_user_setting('VERIFICATION_FLAG_FIELD')
    user = get_user_by_verification_id(data['user_id'], require_verified=False)
    setattr(user, verification_flag_field, True)
    user.save()

    return user

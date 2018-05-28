from django.http import Http404
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_registration.decorators import (
    api_view_serializer_class,
    api_view_serializer_class_getter
)
from rest_registration.exceptions import BadRequest
from rest_registration.notifications import send_verification_notification
from rest_registration.settings import registration_settings
from rest_registration.utils import (
    get_ok_response,
    get_user_by_id,
    get_user_setting,
    verify_signer_or_bad_request
)
from rest_registration.verification import URLParamsSigner


class RegisterSigner(URLParamsSigner):
    salt = 'register'
    use_timestamp = True

    @property
    def base_url(self):
        return registration_settings.REGISTER_VERIFICATION_URL

    @property
    def valid_period(self):
        return registration_settings.REGISTER_VERIFICATION_PERIOD


@api_view_serializer_class_getter(
    lambda: registration_settings.REGISTER_SERIALIZER_CLASS)
@api_view(['POST'])
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

    output_serializer_class = registration_settings.REGISTER_OUTPUT_SERIALIZER_CLASS  # noqa: E501
    output_serializer = output_serializer_class(instance=user)
    user_data = output_serializer.data

    if registration_settings.REGISTER_VERIFICATION_ENABLED:
        signer = RegisterSigner({
            'user_id': user.pk,
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
def verify_registration(request):
    '''
    Verify registration via signature.
    '''
    process_verify_registration_data(request.data)
    return get_ok_response('User verified successfully')


def process_verify_registration_data(input_data):
    if not registration_settings.REGISTER_VERIFICATION_ENABLED:
        raise Http404()
    serializer = VerifyRegistrationSerializer(data=input_data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data
    signer = RegisterSigner(data)
    verify_signer_or_bad_request(signer)

    verification_flag_field = get_user_setting('VERIFICATION_FLAG_FIELD')
    user = get_user_by_id(data['user_id'], require_verified=False)
    setattr(user, verification_flag_field, True)
    user.save()

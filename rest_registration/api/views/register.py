from django.http import Http404
from rest_framework import status
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from rest_registration.notifications import send_verification
from rest_registration.utils import (get_ok_response, get_user_model_class,
                                     get_user_setting,
                                     verify_signer_or_bad_request)
from rest_registration.decorators import serializer_class_getter
from rest_registration.settings import registration_settings
from rest_registration.verification import URLParamsSigner


class RegisterSigner(URLParamsSigner):

    use_timestamp = True

    @property
    def base_url(self):
        return registration_settings.REGISTER_VERIFICATION_URL

    @property
    def valid_period(self):
        return registration_settings.REGISTER_VERIFICATION_PERIOD


@serializer_class_getter(
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

    user = serializer.save(**kwargs)

    profile_serializer_class = registration_settings.PROFILE_SERIALIZER_CLASS
    profile_serializer = profile_serializer_class(instance=user)
    user_data = profile_serializer.data

    if registration_settings.REGISTER_VERIFICATION_ENABLED:
        signer = RegisterSigner({
            'user_id': user.pk,
        }, request=request)
        template_config = (
            registration_settings.REGISTER_VERIFICATION_EMAIL_TEMPLATES)
        send_verification(user, signer, template_config)

    return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyRegistrationSerializer(serializers.Serializer):
    user_id = serializers.CharField(required=True)
    timestamp = serializers.IntegerField(required=True)
    signature = serializers.CharField(required=True)


@api_view(['POST'])
def verify_registration(request):
    '''
    Verify registration via signature.
    ---
    serializer: VerifyRegistrationSerializer
    '''
    if not registration_settings.REGISTER_VERIFICATION_ENABLED:
        raise Http404()
    user_class = get_user_model_class()
    serializer = VerifyRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    data = serializer.data
    signer = RegisterSigner(data, request=request)
    verify_signer_or_bad_request(signer)

    verification_flag_field = get_user_setting('VERIFICATION_FLAG_FIELD')
    user = get_object_or_404(user_class.objects.all(), pk=data['user_id'])
    setattr(user, verification_flag_field, True)
    user.save()

    return get_ok_response('User verified successfully')

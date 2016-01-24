from django.core.signing import BadSignature, SignatureExpired
from django.http import Http404
from rest_framework import status
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_registration.notifications import email as notifications_email
from rest_registration.utils import (get_ok_response, get_user_model_class,
                                     get_user_setting)
from rest_registration.exceptions import BadRequest
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


def _register(request):
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
        email_field = get_user_setting('EMAIL_FIELD')
        email = getattr(user, email_field)
        notifications_email.send(email, signer)

    return Response(user_data, status=status.HTTP_201_CREATED)


class RegisterView(APIView):

    def get_serializer_class(self):
        return get_register_serializer_class()

    def post(self, request):
        return _register(request)


register = RegisterView.as_view()


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
    try:
        signer.verify()
    except SignatureExpired:
        raise BadRequest('Signature expired')
    except BadSignature:
        raise BadRequest('Invalid signature')

    verification_flag_field = get_user_setting('VERIFICATION_FLAG_FIELD')
    user = get_object_or_404(user_class.objects.all(), pk=data['user_id'])
    setattr(user, verification_flag_field, True)
    user.save()

    return get_ok_response('User verified successfully')

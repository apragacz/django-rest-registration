from django.http import Http404
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_registration.decorators import api_view_serializer_class
from rest_registration.notifications import send_verification_notification
from rest_registration.settings import registration_settings
from rest_registration.utils.responses import get_ok_response
from rest_registration.utils.users import get_user_by_id, get_user_setting
from rest_registration.utils.verification import verify_signer_or_bad_request
from rest_registration.verification import URLParamsSigner


class RegisterEmailSigner(URLParamsSigner):
    SALT_BASE = 'register-email'
    USE_TIMESTAMP = True

    def get_base_url(self):
        return registration_settings.REGISTER_EMAIL_VERIFICATION_URL

    def get_valid_period(self):
        return registration_settings.REGISTER_EMAIL_VERIFICATION_PERIOD


class RegisterEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


@api_view_serializer_class(RegisterEmailSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_email(request):
    '''
    Register new email.
    '''
    user = request.user

    serializer = RegisterEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']

    template_config = (
        registration_settings.REGISTER_EMAIL_VERIFICATION_EMAIL_TEMPLATES)
    if registration_settings.REGISTER_EMAIL_VERIFICATION_ENABLED:
        signer = RegisterEmailSigner({
            'user_id': user.pk,
            'email': email,
        }, request=request)
        send_verification_notification(
            user, signer, template_config, email=email)
    else:
        email_field = get_user_setting('EMAIL_FIELD')
        setattr(user, email_field, email)
        user.save()

    return get_ok_response('Register email link email sent')


class VerifyEmailSerializer(serializers.Serializer):
    user_id = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    timestamp = serializers.IntegerField(required=True)
    signature = serializers.CharField(required=True)


@api_view_serializer_class(VerifyEmailSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    '''
    Verify email via signature.
    '''
    process_verify_email_data(request.data)
    return get_ok_response('Email verified successfully')


def process_verify_email_data(input_data):
    if not registration_settings.REGISTER_EMAIL_VERIFICATION_ENABLED:
        raise Http404()
    serializer = VerifyEmailSerializer(data=input_data)
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data
    signer = RegisterEmailSigner(data)
    verify_signer_or_bad_request(signer)

    email_field = get_user_setting('EMAIL_FIELD')
    user = get_user_by_id(data['user_id'])
    setattr(user, email_field, data['email'])
    user.save()

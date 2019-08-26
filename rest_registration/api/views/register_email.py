from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_registration import signals
from rest_registration.decorators import (
    api_view_serializer_class,
    api_view_serializer_class_getter
)
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


class RegisterEmailSigner(URLParamsSigner):
    SALT_BASE = 'register-email'
    USE_TIMESTAMP = True

    def get_base_url(self):
        return registration_settings.REGISTER_EMAIL_VERIFICATION_URL

    def get_valid_period(self):
        return registration_settings.REGISTER_EMAIL_VERIFICATION_PERIOD


@api_view_serializer_class_getter(
    lambda: registration_settings.REGISTER_EMAIL_SERIALIZER_CLASS)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_email(request):
    '''
    Register new email.
    '''
    user = request.user

    serializer_class = registration_settings.REGISTER_EMAIL_SERIALIZER_CLASS
    serializer = serializer_class(
        data=request.data,
        context={'request': request},
    )
    serializer.is_valid(raise_exception=True)

    email = serializer.get_email()

    user_model = get_user_model()
    qs = user_model.objects.filter(email=email)
    if(qs.count() > 0):
        return Response("This email is already registered.")

    template_config = (
        registration_settings.REGISTER_EMAIL_VERIFICATION_EMAIL_TEMPLATES)
    if registration_settings.REGISTER_EMAIL_VERIFICATION_ENABLED:
        signer = RegisterEmailSigner({
            'user_id': get_user_verification_id(user),
            'email': email,
        }, request=request)
        send_verification_notification(
            user, signer, template_config, email=email)
    else:
        email_field = get_user_setting('EMAIL_FIELD')
        old_email = getattr(user, email_field)
        setattr(user, email_field, email)
        user.save()
        signals.user_changed_email.send(
            sender=None,
            user=user,
            new_email=email,
            old_email=old_email,
            request=request,
        )

    return get_ok_response('Register email link email sent')


class VerifyEmailSerializer(serializers.Serializer):  # noqa: E501 pylint: disable=abstract-method
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
    process_verify_email_data(
        request.data, serializer_context={'request': request})
    return get_ok_response('Email verified successfully')


def process_verify_email_data(input_data, serializer_context=None):
    if serializer_context is None:
        serializer_context = {}
    if not registration_settings.REGISTER_EMAIL_VERIFICATION_ENABLED:
        raise Http404()
    serializer = VerifyEmailSerializer(
        data=input_data,
        context=serializer_context,
    )
    serializer.is_valid(raise_exception=True)

    data = serializer.validated_data
    signer = RegisterEmailSigner(data)
    verify_signer_or_bad_request(signer)
    request = serializer_context.get('request')

    email_field = get_user_setting('EMAIL_FIELD')
    user = get_user_by_verification_id(data['user_id'])
    old_email = getattr(user, email_field)
    setattr(user, email_field, data['email'])
    user.save()

    signals.user_changed_email.send(
        sender=None,
        user=user,
        new_email=data['email'],
        old_email=old_email,
        request=request,
    )

from django.http import Http404
from rest_framework import serializers
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404

from rest_registration.exceptions import BadRequest
from rest_registration.notifications import email as notifications_email
from rest_registration.settings import registration_settings
from rest_registration.verification import URLParamsSigner
from rest_registration.utils import (get_ok_response, get_user_model_class,
                                     get_user_setting,
                                     verify_signer_or_bad_request)


class ResetPasswordSigner(URLParamsSigner):

    use_timestamp = True

    @property
    def base_url(self):
        return registration_settings.RESET_PASSWORD_VERIFICATION_URL

    @property
    def valid_period(self):
        return registration_settings.RESET_PASSWORD_VERIFICATION_PERIOD


class SendResetPasswordLinkSerializer(serializers.Serializer):
    login = serializers.CharField(required=True)


def get_login_fields():
    user_class = get_user_model_class()
    return get_user_setting('LOGIN_FIELDS') or [user_class.USERNAME_FIELD]


@api_view(['POST'])
def send_reset_password_link(request):
    serializer = SendResetPasswordLinkSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    login = serializer.data['login']
    user_class = get_user_model_class()
    user_queryset = user_class.objects.all()

    user = None
    for login_field in get_login_fields():
        try:
            user = get_object_or_404(user_queryset, **{login_field: login})
            break
        except Http404:
            pass

    if not user:
        raise BadRequest('User not found')

    signer = ResetPasswordSigner({
        'user_id': user.pk,
    }, request=request)

    email_field = get_user_setting('EMAIL_FIELD')
    email = getattr(user, email_field)
    template_config = (
        registration_settings.RESET_PASSWORD_VERIFICATION_EMAIL_TEMPLATES)
    notifications_email.send(email, signer, template_config)

    return get_ok_response('Reset link sent')


class ResetPasswordSerializer(serializers.Serializer):
    user_id = serializers.CharField(required=True)
    timestamp = serializers.IntegerField(required=True)
    signature = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


@api_view(['POST'])
def reset_password(request):
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    data = serializer.data.copy()
    password = data.pop('password')
    signer = ResetPasswordSigner(data, request=request)
    verify_signer_or_bad_request(signer)

    user_class = get_user_model_class()
    user = get_object_or_404(user_class.objects.all(), pk=data['user_id'])
    user.set_password(password)
    user.save()

    return get_ok_response('Reset password successful')

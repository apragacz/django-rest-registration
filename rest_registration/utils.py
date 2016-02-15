from django.apps import apps
from django.conf import settings
from django.core.signing import BadSignature, SignatureExpired
from rest_framework.response import Response

from rest_registration.exceptions import BadRequest
from rest_registration.settings import registration_settings


def get_user_model_class():
    return apps.get_model(*settings.AUTH_USER_MODEL.rsplit('.', 1))


def get_user_setting(name):
    setting_name = 'USER_{}'.format(name)
    user_class = get_user_model_class()
    placeholder = object()
    value = getattr(user_class, name, placeholder)

    if value is placeholder:
        value = getattr(registration_settings, setting_name)

    return value


def get_ok_response(message, status=200, extra_data=None):
    builder = registration_settings.SUCCESS_RESPONSE_BUILDER
    return builder(message=message, status=status, extra_data=extra_data)


def verify_signer_or_bad_request(signer):
    try:
        signer.verify()
    except SignatureExpired:
        raise BadRequest('Signature expired')
    except BadSignature:
        raise BadRequest('Invalid signature')


def build_default_success_response(message, status, extra_data):
    data = {'detail': message}
    if extra_data:
        data.update(extra_data)
    return Response(data, status=status)

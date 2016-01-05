from django.apps import apps
from django.conf import settings
from rest_framework.response import Response


from .settings import settings as registration_settings


def get_user_model_class():
    return apps.get_model(*settings.AUTH_USER_MODEL.rsplit('.', 1))


def get_user_setting(name):
    setting_name = 'USER_{}'.format(name)
    User = get_user_model_class()
    placeholder = object()
    value = getattr(User, name, placeholder)

    if value is placeholder:
        value = getattr(registration_settings, setting_name)

    return value


def get_ok_response(message, status=200):
    return Response({'detail': message}, status=status)

from django.apps import apps
from django.conf import settings
from rest_framework.response import Response


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


def get_ok_response(message, status=200, extra_data={}):
    data = {'detail': message}
    data.update(extra_data)
    return Response(data, status=status)

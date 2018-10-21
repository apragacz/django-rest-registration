from rest_framework.response import Response

from rest_registration.settings import registration_settings


def get_ok_response(message, status=200, extra_data=None):
    builder = registration_settings.SUCCESS_RESPONSE_BUILDER
    return builder(message=message, status=status, extra_data=extra_data)


def build_default_success_response(message, status, extra_data):
    data = {'detail': message}
    if extra_data:
        data.update(extra_data)
    return Response(data, status=status)

from django.apps import apps
from django.conf import settings
from rest_framework.response import Response


def get_user_model_class():
    return apps.get_model(*settings.AUTH_USER_MODEL.rsplit('.', 1))


def get_ok_response(message, status=200):
    return Response({'detail': message}, status=status)

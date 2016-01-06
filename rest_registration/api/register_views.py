from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from ..utils import get_user_model_class
from .base import get_field_names, get_profile_serializer_class


def generate_register_serializer_class():
    User = get_user_model_class()
    field_names = get_field_names(allow_primary_key=False)
    field_names = field_names + ('password', 'password_confirm')

    class RegisterUserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = field_names

        password_confirm = serializers.CharField()

        def validate(self, data):
            if data['password'] != data['password_confirm']:
                raise ValidationError('Passwords don\'t match')
            del data['password_confirm']
            return data

    return RegisterUserSerializer


def get_register_serializer_class():
    return generate_register_serializer_class()


def _register(request):
    serializer_class = get_register_serializer_class()
    serializer = serializer_class(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.save()

    profile_serializer_class = get_profile_serializer_class()
    profile_serializer = profile_serializer_class(instance=user)

    return Response(profile_serializer.data, status=status.HTTP_201_CREATED)


class RegisterView(APIView):

    def get_serializer_class(self):
        return get_register_serializer_class()

    def post(self, request):
        return _register(request)


register = RegisterView.as_view()

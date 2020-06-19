from django.contrib.auth import get_user_model
from rest_framework import serializers


class DefaultDeprecatedLoginSerializer(serializers.Serializer):  # noqa: E501 pylint: disable=abstract-method
    login = serializers.CharField()
    password = serializers.CharField()

    def get_authenticated_user(self):
        data = self.validated_data
        if data['login'] == 'abra' and data['password'] == 'cadabra':
            user_model = get_user_model()
            return user_model.objects.get()
        return None

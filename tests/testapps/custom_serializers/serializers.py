from django.contrib.auth import get_user_model
from rest_framework import serializers


class DefaultDeprecatedLoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField()

    def get_authenticated_user(self):
        data = self.validated_data
        if data['login'] == 'abra' and data['password'] == 'cadabra':
            user_model = get_user_model()
            return user_model.objects.get()
        return None

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class DefaultDeprecatedSendResetPasswordLinkSerializer(serializers.Serializer):
    login = serializers.CharField(required=True)

    def get_user_or_none(self):
        data = self.validated_data
        if data['login'] == 'abra':
            user_model = get_user_model()
            return user_model.objects.get()
        return None

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

from rest_framework import serializers


class InvalidRegisterEmailSerializer(serializers.Serializer):
    definitely_not_email = serializers.EmailField(required=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

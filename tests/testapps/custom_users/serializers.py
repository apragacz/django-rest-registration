from rest_framework import serializers

from rest_registration.api.serializers import DefaultRegisterUserSerializer
from tests.testapps.custom_users.models import Channel


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ["name", "description"]


class RegisterUserSerializer(DefaultRegisterUserSerializer):
    primary_channel = ChannelSerializer()

    def create(self, validated_data):
        channel_data = validated_data.pop("primary_channel")
        channel = Channel.objects.create(**channel_data)
        validated_data["primary_channel"] = channel
        user = super().create(validated_data)
        return user

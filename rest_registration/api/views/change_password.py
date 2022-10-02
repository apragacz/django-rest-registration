from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _
from rest_framework import permissions, serializers
from rest_framework.request import Request
from rest_framework.response import Response

from rest_registration.api.serializers import PasswordConfirmSerializerMixin
from rest_registration.api.views.base import BaseAPIView
from rest_registration.settings import registration_settings
from rest_registration.utils.responses import get_ok_response
from rest_registration.utils.validation import validate_user_password_confirm


class ChangePasswordSerializer(  # pylint: disable=abstract-method
        PasswordConfirmSerializerMixin,
        serializers.Serializer):
    old_password = serializers.CharField()
    password = serializers.CharField()

    def has_password_confirm_field(self):
        return registration_settings.CHANGE_PASSWORD_SERIALIZER_PASSWORD_CONFIRM

    def validate_old_password(self, old_password):
        user = self.context['request'].user
        if not user.check_password(old_password):
            raise serializers.ValidationError(_("Old password is not correct"))
        return old_password

    def validate_password(self, password):
        user = self.context['request'].user
        validate_password(password, user=user)
        return password

    def validate(self, attrs):
        if self.has_password_confirm_field():
            validate_user_password_confirm(attrs)
        return attrs


class ChangePasswordView(BaseAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        '''
        Change the user password.
        '''
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['password'])
        user.save()
        return get_ok_response(_("Password changed successfully"))


change_password = ChangePasswordView.as_view()

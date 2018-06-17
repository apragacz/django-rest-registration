from django.contrib.auth.password_validation import validate_password
from rest_framework import permissions, serializers
from rest_framework.decorators import api_view, permission_classes

from rest_registration.decorators import api_view_serializer_class
from rest_registration.settings import registration_settings
from rest_registration.utils import get_ok_response


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    password = serializers.CharField()

    @property
    def has_password_confirm(self):
        return registration_settings.CHANGE_PASSWORD_SERIALIZER_PASSWORD_CONFIRM  # noqa: E501

    def validate_old_password(self, old_password):
        user = self.context['request'].user
        if not user.check_password(old_password):
            raise serializers.ValidationError('Old password is not correct')
        return old_password

    def validate_password(self, password):
        user = self.context['request'].user
        validate_password(password, user=user)
        return password

    def get_fields(self):
        fields = super().get_fields()
        if self.has_password_confirm:
            fields['password_confirm'] = serializers.CharField()
        return fields

    def validate(self, data):
        if self.has_password_confirm:
            if data['password'] != data['password_confirm']:
                raise serializers.ValidationError('Passwords don\'t match')
        return data


@api_view_serializer_class(ChangePasswordSerializer)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password(request):
    '''
    Change the user password.
    '''
    serializer = ChangePasswordSerializer(data=request.data,
                                          context={'request': request})
    serializer.is_valid(raise_exception=True)

    user = request.user
    user.set_password(serializer.validated_data['password'])
    user.save()
    return get_ok_response('Password changed successfully')

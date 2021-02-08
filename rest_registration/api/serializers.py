from django.contrib.auth import get_user_model
from rest_framework import serializers

from rest_registration.settings import registration_settings
from rest_registration.utils.users import get_user_public_field_names
from rest_registration.utils.validation import (
    run_validators,
    validate_user_password,
    validate_user_password_confirm
)


class MetaObj:
    pass


class PasswordConfirmSerializerMixin(serializers.Serializer):

    def has_password_confirm_field(self) -> bool:
        raise NotImplementedError()

    def get_fields(self):
        fields = super().get_fields()
        if self.has_password_confirm_field():
            fields['password_confirm'] = serializers.CharField(write_only=True)
        return fields


class DefaultLoginSerializer(serializers.Serializer):  # noqa: E501 pylint: disable=abstract-method
    """
    Default serializer used for user login. Please keep in mind that
    the authentication is done by separate function defined by
    :ref:`login-authenticator-setting` setting.

    By default :ref:`login-authenticator-setting` function will use
    :ref:`user-login-fields-setting` setting to extract the login field
    from the validated serializer data either by using the 'login' key
    (which is used here) or the specific login field name(s)
    (e.g. 'username', 'email').

    If you want different behavior, you need to
    override :ref:`login-authenticator-setting` in your settings.
    """
    login = serializers.CharField()
    password = serializers.CharField()


class DefaultRegisterEmailSerializer(serializers.Serializer):  # noqa: E501 pylint: disable=abstract-method
    """
    Default serializer used for e-mail registration (e-mail change).
    """
    email = serializers.EmailField(required=True)


class DefaultSendResetPasswordLinkSerializer(serializers.Serializer):  # noqa: E501 pylint: disable=abstract-method
    """
    Default serializer used for sending reset password link.

    It will use :ref:`send-reset-password-link-serializer-use-email-setting`
    setting.
    """

    def get_fields(self):
        fields = super().get_fields()
        if registration_settings.SEND_RESET_PASSWORD_LINK_SERIALIZER_USE_EMAIL:
            fields['email'] = serializers.CharField(required=True)
        else:
            fields['login'] = serializers.CharField(required=True)
        return fields


class DefaultUserProfileSerializer(serializers.ModelSerializer):
    """
    Default serializer used for user profile. It will use these:

    * User fields
    * :ref:`user-hidden-fields-setting` setting
    * :ref:`user-public-fields-setting` setting
    * :ref:`user-editable-fields-setting` setting

    to automagically generate the required serializer fields.
    """

    def __init__(self, *args, **kwargs):
        user_class = get_user_model()
        field_names = get_user_public_field_names()
        read_only_field_names = get_user_public_field_names(read_only=True)
        meta_obj = MetaObj()
        meta_obj.model = user_class
        meta_obj.fields = field_names
        meta_obj.read_only_fields = read_only_field_names
        self.Meta = meta_obj  # pylint: disable=invalid-name
        super().__init__(*args, **kwargs)


class DefaultRegisterUserSerializer(
        PasswordConfirmSerializerMixin,
        serializers.ModelSerializer):
    """
    Default serializer used for user registration. It will use these:

    * User fields
    * :ref:`user-hidden-fields-setting` setting
    * :ref:`user-public-fields-setting` setting

    to automagically generate the required serializer fields.
    """

    def __init__(self, *args, **kwargs):
        user_class = get_user_model()
        field_names = get_user_public_field_names(write_once=True)
        read_only_field_names = get_user_public_field_names(
            write_once=True, read_only=True)
        meta_obj = MetaObj()
        meta_obj.model = user_class
        meta_obj.fields = field_names
        meta_obj.read_only_fields = read_only_field_names
        self.Meta = meta_obj  # pylint: disable=invalid-name
        super().__init__(*args, **kwargs)

    def has_password_confirm_field(self):
        return registration_settings.REGISTER_SERIALIZER_PASSWORD_CONFIRM

    def validate(self, attrs):
        validators = [
            validate_user_password,
        ]
        if self.has_password_confirm_field():
            validators.append(validate_user_password_confirm)
        run_validators(validators, attrs)
        return attrs

    def create(self, validated_data):
        data = validated_data.copy()
        if self.has_password_confirm_field():
            del data['password_confirm']
        return self.Meta.model.objects.create_user(**data)

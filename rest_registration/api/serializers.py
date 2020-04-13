from django.contrib.auth import get_user_model
from rest_framework import serializers

from rest_registration.settings import registration_settings
from rest_registration.utils.users import (
    authenticate_by_login_and_password_or_none,
    get_user_by_login_or_none,
    get_user_by_lookup_dict,
    get_user_email_field_name,
    get_user_field_names
)
from rest_registration.utils.validation import (
    run_validators,
    validate_user_password,
    validate_user_password_confirm
)


class MetaObj:  # pylint: disable=too-few-public-methods
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
    Default serializer used for user login. It will use
    :ref:`user-login-fields-setting` setting to compare the login
    to the user login fields defined by this setting.
    """
    login = serializers.CharField()
    password = serializers.CharField()

    def get_authenticated_user(self):
        """
        Return authenticated user if login and password match.
        Return ``None`` otherwise.
        """
        data = self.validated_data
        return authenticate_by_login_and_password_or_none(
            data['login'], data['password'])


class DefaultRegisterEmailSerializer(serializers.Serializer):  # noqa: E501 pylint: disable=abstract-method
    """
    Default serializer used for e-mail registration (e-mail change).
    """
    email = serializers.EmailField(required=True)

    def get_email(self):
        """
        Return user email.
        """
        return self.validated_data['email']


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

    def get_user_or_none(self):
        """
        Return user if matching given criteria (login fields / e-mail).
        Return ``None`` otherwise.
        """
        if registration_settings.SEND_RESET_PASSWORD_LINK_SERIALIZER_USE_EMAIL:
            email = self.validated_data['email']
            return self._get_user_by_email_or_none(email)
        login = self.validated_data['login']
        return self._get_user_by_login_or_none(login)

    def _get_user_by_login_or_none(self, login):
        return get_user_by_login_or_none(login)

    def _get_user_by_email_or_none(self, email):
        email_field_name = get_user_email_field_name()
        return get_user_by_lookup_dict(
            {email_field_name: email}, default=None, require_verified=False)


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
        field_names = get_user_field_names(allow_primary_key=True)
        read_only_field_names = get_user_field_names(
            allow_primary_key=True,
            non_editable=True)
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
        field_names = get_user_field_names(allow_primary_key=True)
        field_names = field_names + ('password',)
        read_only_field_names = get_user_field_names(
            allow_primary_key=True,
            non_editable=True)
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

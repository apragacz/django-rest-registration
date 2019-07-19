from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from rest_registration.settings import registration_settings
from rest_registration.utils.users import (
    authenticate_by_login_and_password_or_none,
    get_user_by_lookup_dict,
    get_user_login_fields,
    get_user_setting
)


class MetaObj:  # pylint: disable=too-few-public-methods
    pass


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
        user = None
        for login_field in get_user_login_fields():
            user = get_user_by_lookup_dict(
                {login_field: login}, default=None, require_verified=False)
            if user:
                break

        return user

    def _get_user_by_email_or_none(self, email):
        email_field = get_user_setting('EMAIL_FIELD')
        return get_user_by_lookup_dict(
            {email_field: email}, default=None, require_verified=False)


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
        field_names = _get_field_names(allow_primary_key=True)
        read_only_field_names = _get_field_names(
            allow_primary_key=True,
            non_editable=True)
        meta_obj = MetaObj()
        meta_obj.model = user_class
        meta_obj.fields = field_names
        meta_obj.read_only_fields = read_only_field_names
        self.Meta = meta_obj  # pylint: disable=invalid-name
        super().__init__(*args, **kwargs)


class DefaultRegisterUserSerializer(serializers.ModelSerializer):
    """
    Default serializer used for user registration. It will use these:

    * User fields
    * :ref:`user-hidden-fields-setting` setting
    * :ref:`user-public-fields-setting` setting

    to automagically generate the required serializer fields.
    """

    def __init__(self, *args, **kwargs):
        user_class = get_user_model()
        field_names = _get_field_names(allow_primary_key=True)
        field_names = field_names + ('password',)
        read_only_field_names = _get_field_names(
            allow_primary_key=True,
            non_editable=True)
        meta_obj = MetaObj()
        meta_obj.model = user_class
        meta_obj.fields = field_names
        meta_obj.read_only_fields = read_only_field_names
        self.Meta = meta_obj  # pylint: disable=invalid-name
        super().__init__(*args, **kwargs)

    @property
    def has_password_confirm(self):
        return registration_settings.REGISTER_SERIALIZER_PASSWORD_CONFIRM

    def validate_password(self, password):
        user = _build_initial_user(self.initial_data)
        validate_password(password, user=user)
        return password

    def get_fields(self):
        fields = super().get_fields()
        if self.has_password_confirm:
            fields['password_confirm'] = serializers.CharField(write_only=True)
        return fields

    def validate(self, attrs):
        if self.has_password_confirm:
            if attrs['password'] != attrs['password_confirm']:
                raise ValidationError('Passwords don\'t match')
        return attrs

    def create(self, validated_data):
        data = validated_data.copy()
        if self.has_password_confirm:
            del data['password_confirm']
        return self.Meta.model.objects.create_user(**data)


def _build_initial_user(data):
    user_field_names = _get_field_names(allow_primary_key=False)
    user_data = {}
    for field_name in user_field_names:
        if field_name in data:
            user_data[field_name] = data[field_name]
    user_class = get_user_model()
    return user_class(**user_data)


def _get_field_names(allow_primary_key=True, non_editable=False):

    def not_in_seq(names):
        return lambda name: name not in names

    user_class = get_user_model()
    fields = user_class._meta.get_fields()  # pylint: disable=protected-access
    default_field_names = [f.name for f in fields
                           if (getattr(f, 'serialize', False) or
                               getattr(f, 'primary_key', False))]
    pk_field_names = [f.name for f in fields
                      if getattr(f, 'primary_key', False)]
    hidden_field_names = set(get_user_setting('HIDDEN_FIELDS'))
    hidden_field_names = hidden_field_names.union(['last_login', 'password'])
    public_field_names = get_user_setting('PUBLIC_FIELDS')
    editable_field_names = get_user_setting('EDITABLE_FIELDS')

    field_names = (public_field_names if public_field_names is not None
                   else default_field_names)
    if editable_field_names is None:
        editable_field_names = field_names

    editable_field_names = set(filter(not_in_seq(pk_field_names),
                                      editable_field_names))

    field_names = filter(not_in_seq(hidden_field_names), field_names)
    if not allow_primary_key:
        field_names = filter(not_in_seq(pk_field_names), field_names)

    if non_editable:
        field_names = filter(not_in_seq(editable_field_names), field_names)

    field_names = tuple(field_names)

    return field_names

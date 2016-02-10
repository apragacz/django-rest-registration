from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from rest_registration.utils import get_user_model_class, get_user_setting


class MetaObj(object):
    pass


class DefaultUserProfileSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        user_class = get_user_model_class()
        field_names = _get_field_names(allow_primary_key=True)
        readonly_field_names = _get_field_names(allow_primary_key=False,
                                                non_editable=True)
        self.Meta = MetaObj()
        self.Meta.model = user_class
        self.Meta.fields = field_names
        self.Meta.readonly_fields = readonly_field_names
        super().__init__(*args, **kwargs)


class DefaultRegisterUserSerializer(serializers.ModelSerializer):

    password_confirm = serializers.CharField()

    def __init__(self, *args, **kwargs):
        user_class = get_user_model_class()
        field_names = _get_field_names(allow_primary_key=False)
        field_names = field_names + ('password', 'password_confirm')
        self.Meta = MetaObj()
        self.Meta.model = user_class
        self.Meta.fields = field_names
        super().__init__(*args, **kwargs)

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise ValidationError('Passwords don\'t match')
        return data

    def create(self, validated_data):
        data = validated_data.copy()
        del data['password_confirm']
        return self.Meta.model.objects.create_user(**data)


def _get_field_names(allow_primary_key=True, non_editable=False):

    def not_in_seq(names):
        return lambda name: name not in names

    user_class = get_user_model_class()
    fields = user_class._meta.get_fields()
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

    editable_field_names = filter(not_in_seq(pk_field_names),
                                  editable_field_names)

    field_names = filter(not_in_seq(hidden_field_names), field_names)
    if not allow_primary_key:
        field_names = filter(not_in_seq(pk_field_names), field_names)

    if non_editable:
        field_names = filter(not_in_seq(editable_field_names), field_names)

    field_names = tuple(field_names)

    return field_names

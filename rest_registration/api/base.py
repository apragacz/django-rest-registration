from rest_framework import serializers

from ..utils import get_user_model_class, get_user_setting


def get_field_names(allow_primary_key=True):

    def in_seq(names):
        return lambda name: name in names

    def not_in_seq(names):
        return lambda name: name not in names

    User = get_user_model_class()
    fields = User._meta.get_fields()
    hidden_field_names = set(get_user_setting('HIDDEN_FIELDS'))
    hidden_field_names = hidden_field_names.union(['last_login', 'password', 'logentry'])
    public_field_names = get_user_setting('PUBLIC_FIELDS')
    pk_field_names = [f.name for f in fields
                      if getattr(f, 'primary_key', False)]

    field_names = (f.name for f in fields)

    if public_field_names is not None:
        field_names = filter(in_seq(public_field_names), field_names)

    field_names = filter(not_in_seq(hidden_field_names), field_names)

    if not allow_primary_key:
        field_names = filter(not_in_seq(pk_field_names), field_names)

    field_names = tuple(field_names)

    return field_names


def generate_profile_serializer_class():
    User = get_user_model_class()
    field_names = get_field_names(allow_primary_key=True)

    class UserProfileSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = field_names
            readonly_fields = field_names

    return UserProfileSerializer


def get_profile_serializer_class():
    return generate_profile_serializer_class()

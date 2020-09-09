from typing import TYPE_CHECKING, Any, Dict

from django.contrib import auth
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404 as _get_object_or_404

from rest_registration.exceptions import UserNotFound
from rest_registration.settings import registration_settings

_RAISE_EXCEPTION = object()

if TYPE_CHECKING:
    from typing import List
    from django.contrib.auth.base_user import AbstractBaseUser


def get_user_by_login_or_none(login, require_verified=False):
    user = None
    for login_field_name in get_user_login_field_names():
        user = get_user_by_lookup_dict(
            {login_field_name: login},
            default=None, require_verified=require_verified)
        if user:
            break

    return user


def authenticate_by_login_data(
        data: Dict[str, Any], **kwargs) -> 'AbstractBaseUser':
    serializer = kwargs.get('serializer')
    if serializer:
        # TODO: Issue #114 - remove code supporting deprecated behavior
        get_authenticated_user = getattr(
            serializer, 'get_authenticated_user', None)
        if callable(get_authenticated_user):
            user = get_authenticated_user()
            if not user:
                raise UserNotFound()
            return user

    login_field_names = get_user_login_field_names()
    password = data.get('password')
    login = data.get('login')
    if password is None:
        raise UserNotFound()
    auth_tests = []  # type: List[Dict[str, Any]]
    if login is not None:
        auth_tests.extend({
            field_name: login,
            'password': password,
        } for field_name in login_field_names)

    for field_name in login_field_names:
        field_value = data.get(field_name)
        if field_value is None:
            continue
        auth_tests.append({
            field_name: field_value,
            'password': password,
        })

    for auth_kwargs in auth_tests:
        user = auth.authenticate(**auth_kwargs)
        if user:
            return user

    raise UserNotFound()


def get_user_login_field_names():
    user_class = get_user_model()
    return get_user_setting('LOGIN_FIELDS') or [user_class.USERNAME_FIELD]


def get_user_verification_id(user):
    verification_id_field = get_user_setting('VERIFICATION_ID_FIELD')
    return getattr(user, verification_id_field)


def get_user_by_verification_id(
        user_verification_id, default=_RAISE_EXCEPTION, require_verified=True):
    verification_id_field = get_user_setting('VERIFICATION_ID_FIELD')
    return get_user_by_lookup_dict({
        verification_id_field: user_verification_id},
        default=default,
        require_verified=require_verified)


def user_with_email_exists(email):
    user_class = get_user_model()
    email_field_name = get_user_email_field_name()
    if not email_field_name:
        return True
    queryset = user_class.objects.filter(**{email_field_name: email})
    return queryset.exists()


def is_user_email_field_unique():
    email_field_name = get_user_email_field_name()
    email_field = get_user_field_obj(email_field_name)
    return is_model_field_unique(email_field)


def get_user_email_field_name():
    return get_user_setting('EMAIL_FIELD')


def get_user_by_lookup_dict(
        lookup_dict, default=_RAISE_EXCEPTION, require_verified=True):
    verification_enabled = registration_settings.REGISTER_VERIFICATION_ENABLED
    verification_flag_field = get_user_setting('VERIFICATION_FLAG_FIELD')
    user_class = get_user_model()
    kwargs = {}
    kwargs.update(lookup_dict)
    if require_verified and verification_enabled and verification_flag_field:
        kwargs[verification_flag_field] = True
    try:
        user = get_object_or_404(user_class.objects.all(), **kwargs)
    except Http404:
        if default is _RAISE_EXCEPTION:
            raise UserNotFound() from None
        return default
    else:
        return user


def get_user_field_obj(name):
    user_class = get_user_model()
    return user_class._meta.get_field(name)  # pylint: disable=protected-access


def get_user_setting(name):
    setting_name = 'USER_{name}'.format(name=name)
    user_class = get_user_model()
    placeholder = object()
    value = getattr(user_class, name, placeholder)

    if value is placeholder:
        value = getattr(registration_settings, setting_name)

    return value


def build_initial_user(data: Dict[str, Any]) -> 'AbstractBaseUser':
    user_field_names = get_user_field_names(allow_primary_key=False)
    user_data = {}
    for field_name in user_field_names:
        if field_name in data:
            user_data[field_name] = data[field_name]
    user_class = get_user_model()
    return user_class(**user_data)


def get_user_field_names(
        allow_primary_key: bool = True, non_editable: bool = False):

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


def is_model_field_unique(field):
    return field.unique or field.primary_key


def get_object_or_404(queryset, *filter_args, **filter_kwargs):
    """
    Same as Django's standard shortcut, but make sure to also raise 404
    if the filter_kwargs don't match the required types.

    This function was copied from rest_framework.generics because of issue #36.
    """
    try:
        return _get_object_or_404(queryset, *filter_args, **filter_kwargs)
    except (TypeError, ValueError, ValidationError):
        raise Http404 from None

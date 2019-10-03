from django.contrib import auth
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404 as _get_object_or_404

from rest_registration.exceptions import UserNotFound
from rest_registration.settings import registration_settings

_RAISE_EXCEPTION = object()


def get_user_by_login_or_none(login, require_verified=False):
    user = None
    for login_field_name in get_user_login_field_names():
        user = get_user_by_lookup_dict(
            {login_field_name: login},
            default=None, require_verified=require_verified)
        if user:
            break

    return user


def authenticate_by_login_and_password_or_none(login, password):
    user = None
    login_field_names = get_user_login_field_names()

    for field_name in login_field_names:
        kwargs = {
            field_name: login,
            'password': password,
        }
        user = auth.authenticate(**kwargs)
        if user:
            break

    return user


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
    email_field = get_user_setting('EMAIL_FIELD')
    if not email_field:
        return True
    queryset = user_class.objects.filter(**{email_field: email})
    return queryset.exists()


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
            raise UserNotFound()
        return default
    else:
        return user


def get_user_setting(name):
    setting_name = 'USER_{name}'.format(name=name)
    user_class = get_user_model()
    placeholder = object()
    value = getattr(user_class, name, placeholder)

    if value is placeholder:
        value = getattr(registration_settings, setting_name)

    return value


def get_object_or_404(queryset, *filter_args, **filter_kwargs):
    """
    Same as Django's standard shortcut, but make sure to also raise 404
    if the filter_kwargs don't match the required types.

    This function was copied from rest_framework.generics because of issue #36.
    """
    try:
        return _get_object_or_404(queryset, *filter_args, **filter_kwargs)
    except (TypeError, ValueError, ValidationError):
        raise Http404

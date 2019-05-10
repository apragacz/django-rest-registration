from django.contrib import auth
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404 as _get_object_or_404

from rest_registration.exceptions import UserNotFound
from rest_registration.settings import registration_settings

_RAISE_EXCEPTION = object()


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


def get_user_login_fields():
    user_class = get_user_model()
    return get_user_setting('LOGIN_FIELDS') or [user_class.USERNAME_FIELD]


def get_user_setting(name):
    setting_name = 'USER_{name}'.format(name=name)
    user_class = get_user_model()
    placeholder = object()
    value = getattr(user_class, name, placeholder)

    if value is placeholder:
        value = getattr(registration_settings, setting_name)

    return value


def authenticate_by_login_and_password_or_none(login, password):
    user = None
    login_fields = get_user_login_fields()

    for field_name in login_fields:
        kwargs = {
            field_name: login,
            'password': password,
        }
        user = auth.authenticate(**kwargs)
        if user:
            break

    return user


def get_user_by_id(user_id, default=_RAISE_EXCEPTION, require_verified=True):
    return get_user_by_lookup_dict({
        'pk': user_id,
    }, require_verified=require_verified)


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
        else:
            return default
    else:
        return user
